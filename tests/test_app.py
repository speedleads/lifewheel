"""Run with installed application dependencies: python -m unittest discover -s tests."""
import unittest
from streamlit.testing.v1 import AppTest


class AppTests(unittest.TestCase):
    def test_start_save_and_compare(self):
        app = AppTest.from_file("streamlit_app.py").run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.slider), 10)
        self.assertTrue(all(slider.proto.min == 0 and slider.proto.max == 10 for slider in app.slider))
        app.button[0].click().run()
        self.assertIn("My Life Wheel", app.session_state["saved_wheels"])
        app.text_input[0].set_value("Second").run()
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.multiselect[0].value), 2)
        self.assertEqual(app.multiselect[0].proto.max_selections, 3)
        app.button[0].click().run()
        self.assertTrue(app.error)
        self.assertEqual(len(app.session_state["saved_wheels"]), 2)

    def test_empty_name(self):
        app = AppTest.from_file("streamlit_app.py").run()
        app.text_input[0].set_value(" ").run()
        app.button[0].click().run()
        self.assertTrue(app.error)
        self.assertEqual(app.session_state["saved_wheels"], {})
