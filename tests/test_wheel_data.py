import json
import unittest

from wheel_data import CATEGORIES, export_assessments, import_assessments, validate_assessments


class AssessmentTests(unittest.TestCase):
    def setUp(self):
        self.saved = {"First": [0, 10, 2.5, 3, 4, 5, 6, 7, 8, 9]}

    def test_categories_and_valid_scores(self):
        self.assertEqual(len(CATEGORIES), 10)
        validated = validate_assessments(self.saved)
        self.assertEqual(validated, self.saved)
        validated["First"][0] = 5
        self.assertEqual(self.saved["First"][0], 0)

    def test_round_trip_all_assessments_and_unicode(self):
        saved = {**self.saved, "Été": [5] * 10, "Third": [10] * 10}
        payload = export_assessments(saved)
        self.assertEqual(json.loads(payload), saved)
        self.assertEqual(import_assessments(payload.encode("utf-8"), {}), saved)

    def test_empty_export(self):
        self.assertEqual(import_assessments(export_assessments({}), {}), {})

    def test_invalid_structure_and_names(self):
        for data in ([], None, 5, {"": [5] * 10}, {"  ": [5] * 10}, {2: [5] * 10}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                validate_assessments(data)

    def test_invalid_count_and_score_container(self):
        for scores in ([], [5] * 9, [5] * 11, "1234567890", {str(i): 5 for i in range(10)}):
            with self.subTest(scores=scores), self.assertRaises(ValueError):
                validate_assessments({"Bad": scores})

    def test_invalid_score_types_and_ranges(self):
        for score in (True, False, "5", None, [], {}, -1, 10.1, float("nan"), float("inf"), float("-inf"), 10**400):
            with self.subTest(score=score), self.assertRaises(ValueError):
                validate_assessments({"Bad": [score] + [5] * 9})

    def test_malformed_json_and_encoding(self):
        for payload in ('{', '{"x": [}', b'\xff', '[' * 2000, None):
            with self.subTest(payload=repr(payload)[:50]), self.assertRaises(ValueError):
                import_assessments(payload, self.saved)

    def test_duplicate_keys_rejected(self):
        payload = '{"Same": ' + json.dumps([5] * 10) + ', "Same": ' + json.dumps([6] * 10) + '}'
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            import_assessments(payload, {})

    def test_conflicts_reject_entire_import_without_mutation(self):
        payload = export_assessments({"New": [5] * 10, "First": [6] * 10})
        original = export_assessments(self.saved)
        with self.assertRaisesRegex(ValueError, "overwrite"):
            import_assessments(payload, self.saved)
        self.assertEqual(export_assessments(self.saved), original)

    def test_invalid_assessment_rejects_entire_import(self):
        payload = json.dumps({"New": [5] * 10, "Bad": [11] * 10})
        with self.assertRaises(ValueError):
            import_assessments(payload, self.saved)
        self.assertEqual(list(self.saved), ["First"])

    def test_merge_preserves_existing_and_copies(self):
        merged = import_assessments(export_assessments({"New": [5] * 10}), self.saved)
        self.assertEqual(list(merged), ["First", "New"])
        merged["First"][0] = 7
        self.assertEqual(self.saved["First"][0], 0)

    def test_export_validates(self):
        with self.assertRaises(ValueError):
            export_assessments({"Bad": [12] * 10})


if __name__ == "__main__":
    unittest.main()
