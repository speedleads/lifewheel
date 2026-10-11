"""Verify the actual Streamlit server starts, responds, and shuts down."""
import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request


class ServerTests(unittest.TestCase):
    def test_headless_server_health(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        with tempfile.TemporaryFile(mode="w+") as log:
            process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
                 "--server.headless=true", "--server.address=127.0.0.1",
                 f"--server.port={port}", "--browser.gatherUsageStats=false"],
                stdout=log, stderr=subprocess.STDOUT,
                env={**os.environ, "MPLBACKEND": "Agg"},
            )
            try:
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                deadline = time.monotonic() + 20
                while time.monotonic() < deadline and process.poll() is None:
                    try:
                        with opener.open(f"http://127.0.0.1:{port}/_stcore/health", timeout=1) as response:
                            self.assertEqual(response.status, 200)
                            self.assertEqual(response.read(), b"ok")
                            return
                    except (urllib.error.URLError, TimeoutError):
                        time.sleep(0.1)
                log.seek(0)
                self.fail("Streamlit did not become healthy:\n" + log.read())
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
