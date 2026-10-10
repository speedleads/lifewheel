# Life Wheel v0.1

A simple Streamlit app for scoring ten areas of life from 0 to 10, saving named
assessments, and comparing up to three assessments on a radar chart.

## Install and launch

Use Python 3.10–3.12 (Python 3.12 recommended).

```sh
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Open the local URL printed by Streamlit (normally http://localhost:8501).
Direct application dependencies are pinned to compatible versions in requirements.txt.

## Usage

1. Enter a wheel name in the sidebar, adjust the ten sliders, and select **Save This Wheel**.
   Blank names and existing names are rejected; use a new name for another assessment.
2. Once at least two wheels are saved, choose up to three in **Compare Saved Wheels**.
   The radar scale stays fixed at 0–10. All saved wheels also appear in the table.
3. Select **Download All Wheels as JSON** to back up every saved assessment.
4. Upload a previous export and select **Import Wheels**. The whole file is validated
   before any assessment is added. Errors leave saved assessments unchanged.
   Name collisions are rejected; rename conflicting entries in the file or use a fresh session.

Assessments live only in the current Streamlit session. Download a backup before
closing or refreshing the session or restarting the app. There is no database or
automatic disk storage, and importing never deletes or overwrites existing data.

## JSON format

Exports retain the original mapping of names to ordered score arrays:

```json
{"My Life Wheel": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]}
```

The ten scores correspond, in order, to Spirituality, Money & Finance, Career & Work,
Health & Fitness, Fun & Recreation, Environment, Community, Family & Friends,
Partner & Love, and Growth & Learning. Scores must be finite JSON numbers from 0 to 10;
fractional scores are accepted on import. Strings, booleans, incorrect score counts,
blank names, duplicate JSON names, invalid UTF-8, and malformed JSON are rejected.
An empty object is a valid export of an empty session.

## Tests

With dependencies installed, run all data and Streamlit smoke tests:

```sh
python -m unittest discover -s tests -v
```

The pure validation and serialization tests also run without application dependencies:

```sh
python -m unittest discover -s tests -p test_wheel_data.py -v
```

The tests use in-memory assessments and do not create or change user data files.
