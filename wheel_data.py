"""Pure validation and JSON serialization for named Life Wheel assessments."""
import json
import math

CATEGORIES = (
    "Spirituality", "Money & Finance", "Career & Work", "Health & Fitness",
    "Fun & Recreation", "Environment", "Community", "Family & Friends",
    "Partner & Love", "Growth & Learning",
)


def validate_assessments(data):
    """Return a validated copy of a name-to-scores mapping."""
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object mapping assessment names to scores.")
    result = {}
    for name, scores in data.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Assessment names must be non-empty strings.")
        if not isinstance(scores, list) or len(scores) != len(CATEGORIES):
            raise ValueError(f"Assessment '{name}' must have exactly {len(CATEGORIES)} scores.")
        for score in scores:
            if type(score) not in (int, float):
                raise ValueError(f"Assessment '{name}' scores must be numbers, not booleans or strings.")
            if not 0 <= score <= 10 or (isinstance(score, float) and not math.isfinite(score)):
                raise ValueError(f"Assessment '{name}' scores must be finite numbers from 0 to 10.")
        result[name] = scores.copy()
    return result


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate assessment name '{key}' in JSON.")
        result[key] = value
    return result


def import_assessments(payload, existing):
    """Validate the whole file and merge atomically, rejecting name collisions."""
    try:
        incoming = json.loads(payload, object_pairs_hook=_unique_object)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError, RecursionError) as exc:
        raise ValueError("Invalid JSON file. Upload a UTF-8 Life Wheel JSON export.") from exc
    incoming = validate_assessments(incoming)
    merged = validate_assessments(existing)
    conflicts = merged.keys() & incoming.keys()
    if conflicts:
        raise ValueError("Import would overwrite existing assessments: " + ", ".join(sorted(conflicts))
                         + ". Rename the assessments in the file before importing.")
    merged.update(incoming)
    return merged


def export_assessments(assessments):
    """Serialize every saved assessment in the original export format."""
    return json.dumps(validate_assessments(assessments), indent=2, ensure_ascii=False, allow_nan=False)
