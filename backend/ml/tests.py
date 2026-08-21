"""Unit tests for the ML pipeline modules."""
from types import SimpleNamespace

from django.test import TestCase

from ml.clustering import complementary_match, k_means_cluster, recommended_group_count
from ml.preprocessing import clean_scores, infer_learning_preference
from ml.quality import (
    detect_duplicates,
    elbow_inertias,
    evaluate_clustering,
    missing_scores,
    optimal_k_by_elbow,
    silhouette_value,
    standardize_matrix,
)
from ml.strength_analysis import detect_strengths, detect_weaknesses


def make_student(pk: int, scores: dict):
    return SimpleNamespace(
        pk=pk,
        id=pk,
        full_name=f'Student {pk}',
        scores=scores,
        strengths=[],
        weaknesses=[],
    )


class StrengthThresholdTests(TestCase):
    def test_score_of_75_is_a_strength(self):
        scores = {'Mathematics': 75, 'Physics': 60, 'Programming': 40, 'Database': 30, 'Operating Systems': 20}
        self.assertEqual(detect_strengths(scores), ['Mathematics'])

    def test_score_below_75_is_not_a_strength(self):
        scores = {'Mathematics': 74, 'Physics': 90, 'Programming': 40, 'Database': 30, 'Operating Systems': 20}
        self.assertEqual(detect_strengths(scores), ['Physics'])

    def test_score_of_50_is_a_weakness(self):
        scores = {'Mathematics': 50, 'Physics': 90, 'Programming': 40, 'Database': 30, 'Operating Systems': 20}
        self.assertEqual(detect_weaknesses(scores), ['Operating Systems', 'Database', 'Programming'])

    def test_score_below_50_is_a_weakness(self):
        scores = {'Mathematics': 49, 'Physics': 90, 'Programming': 70, 'Database': 60, 'Operating Systems': 55}
        self.assertEqual(detect_weaknesses(scores), ['Mathematics'])

    def test_mid_range_scores_are_neither_strength_nor_weakness(self):
        scores = {'Mathematics': 60, 'Physics': 70, 'Programming': 65, 'Database': 55, 'Operating Systems': 74}
        self.assertEqual(detect_strengths(scores), [])
        self.assertEqual(detect_weaknesses(scores), [])


class GroupCountTests(TestCase):
    def test_recommended_counts_keep_groups_between_three_and_four(self):
        cases = {
            4: 1,
            5: 1,
            6: 2,
            7: 2,
            8: 2,
            9: 3,
            10: 3,
            11: 3,
            12: 3,
            14: 4,
            16: 4,
            18: 5,
            20: 5,
        }
        for count, expected in cases.items():
            with self.subTest(count=count):
                self.assertEqual(recommended_group_count(count), expected)

    def test_zero_students_yield_zero_groups(self):
        self.assertEqual(recommended_group_count(0), 0)


class PreprocessingTests(TestCase):
    def test_clean_scores_clamps_and_coerces(self):
        cleaned = clean_scores({'Mathematics': 120, 'Physics': -5, 'Programming': '78', 'Database': None, 'Operating Systems': 'abc'})
        self.assertEqual(cleaned['Mathematics'], 100.0)
        self.assertEqual(cleaned['Physics'], 0.0)
        self.assertEqual(cleaned['Programming'], 78.0)
        self.assertEqual(cleaned['Database'], 0.0)
        self.assertEqual(cleaned['Operating Systems'], 0.0)

    def test_infer_learning_preference(self):
        self.assertEqual(
            infer_learning_preference({'Programming': 90, 'Database': 85, 'Mathematics': 50, 'Physics': 40, 'Operating Systems': 30}),
            'Practical',
        )
        self.assertEqual(
            infer_learning_preference({'Mathematics': 90, 'Physics': 85, 'Programming': 40, 'Database': 40, 'Operating Systems': 30}),
            'Theory',
        )
        self.assertEqual(
            infer_learning_preference({'Mathematics': 60, 'Physics': 60, 'Programming': 60, 'Database': 60, 'Operating Systems': 60}),
            'Mixed',
        )


class ClusteringTests(TestCase):
    def test_k_means_returns_one_label_per_row(self):
        rows = [[90, 80, 85, 75, 70], [40, 45, 50, 55, 60], [88, 82, 90, 78, 72], [42, 40, 44, 50, 55]]
        labels = k_means_cluster(rows, target_size=4)
        self.assertEqual(len(labels), 4)

    def test_complementary_match_assigns_every_student_exactly_once(self):
        students = [
            make_student(1, {'Mathematics': 90, 'Physics': 40, 'Programming': 45, 'Database': 40, 'Operating Systems': 40}),
            make_student(2, {'Mathematics': 40, 'Physics': 88, 'Programming': 45, 'Database': 40, 'Operating Systems': 40}),
            make_student(3, {'Mathematics': 40, 'Physics': 40, 'Programming': 90, 'Database': 40, 'Operating Systems': 40}),
            make_student(4, {'Mathematics': 40, 'Physics': 40, 'Programming': 45, 'Database': 88, 'Operating Systems': 40}),
            make_student(5, {'Mathematics': 40, 'Physics': 40, 'Programming': 45, 'Database': 40, 'Operating Systems': 90}),
            make_student(6, {'Mathematics': 70, 'Physics': 70, 'Programming': 70, 'Database': 70, 'Operating Systems': 70}),
            make_student(7, {'Mathematics': 80, 'Physics': 30, 'Programming': 80, 'Database': 30, 'Operating Systems': 30}),
            make_student(8, {'Mathematics': 30, 'Physics': 80, 'Programming': 30, 'Database': 80, 'Operating Systems': 30}),
        ]
        labels = k_means_cluster([[float(scores[s]) for s in ['Mathematics', 'Physics', 'Programming', 'Database', 'Operating Systems']] for scores in [s.scores for s in students]], target_size=4)
        groups = complementary_match(students, labels, target_size=4)
        assigned = [member.pk for group in groups for member in group]
        self.assertEqual(sorted(assigned), sorted([1, 2, 3, 4, 5, 6, 7, 8]))
        self.assertEqual(sum(len(group) for group in groups), 8)


class ClusteringQualityTests(TestCase):
    def test_standardize_matrix_centers_and_scales(self):
        rows = [[10, 20], [20, 30], [30, 40], [40, 50]]
        scaled = standardize_matrix(rows)
        self.assertEqual(scaled.shape, (4, 2))
        self.assertAlmostEqual(float(scaled.mean()), 0.0, places=6)
        self.assertAlmostEqual(float(scaled.std()), 1.0, places=6)

    def test_standardize_matrix_falls_back_on_zero_variance(self):
        rows = [[60, 60], [60, 60]]
        scaled = standardize_matrix(rows)
        self.assertEqual(scaled.tolist(), rows)

    def test_elbow_inertias_are_descending_and_start_at_one(self):
        rows = [[90, 80], [85, 75], [50, 40], [45, 35], [10, 20], [15, 25], [30, 30], [28, 32]]
        curve = elbow_inertias(rows, max_k=5)
        self.assertEqual(curve[0]['k'], 1)
        for previous, current in zip(curve, curve[1:]):
            self.assertGreaterEqual(previous['inertia'], current['inertia'])

    def test_optimal_k_by_elbow_returns_a_plausible_k(self):
        rows = [[90, 80], [85, 75], [88, 78], [50, 40], [45, 35], [48, 42], [10, 20], [15, 25], [12, 22]]
        k = optimal_k_by_elbow(rows, max_k=5)
        self.assertGreaterEqual(k, 1)
        self.assertLessEqual(k, 5)

    def test_silhouette_value_is_computable_for_well_separated_clusters(self):
        rows = [[0, 0], [0.5, 0.5], [1, 1], [20, 20], [21, 21], [22, 22]]
        labels = [0, 0, 0, 1, 1, 1]
        score = silhouette_value(rows, labels)
        self.assertIsNotNone(score)
        self.assertGreater(score, 0.5)

    def test_silhouette_value_is_none_for_single_cluster(self):
        rows = [[1, 2], [3, 4], [5, 6]]
        self.assertIsNone(silhouette_value(rows, [0, 0, 0]))

    def test_evaluate_clustering_reports_sizes_and_metrics(self):
        rows = [[0, 0], [1, 1], [20, 20], [21, 21]]
        quality = evaluate_clustering(rows, [0, 0, 1, 1])
        self.assertEqual(quality['k'], 2)
        self.assertEqual(quality['minGroupSize'], 2)
        self.assertEqual(quality['maxGroupSize'], 2)
        self.assertIsNotNone(quality['inertia'])
        self.assertIsNotNone(quality['silhouette'])

    def test_k_means_can_attach_quality_payload(self):
        rows = [[0, 0], [1, 1], [20, 20], [21, 21], [40, 40], [41, 41]]
        labels = k_means_cluster(rows, cluster_count=3, use_scaler=True, include_quality=True)
        self.assertEqual(len(labels), 6)
        quality = getattr(labels, 'quality', None)
        self.assertIsNotNone(quality)
        self.assertEqual(quality['k'], 3)


class DataHygieneTests(TestCase):
    def test_detect_duplicates_flags_duplicate_ids_and_profiles(self):
        students = [
            make_student(1, {'Mathematics': 90, 'Physics': 80, 'Programming': 85, 'Database': 75, 'Operating Systems': 70}),
            make_student(2, {'Mathematics': 90, 'Physics': 80, 'Programming': 85, 'Database': 75, 'Operating Systems': 70}),
            make_student(3, {'Mathematics': 90, 'Physics': 80, 'Programming': 85, 'Database': 75, 'Operating Systems': 70}),
        ]
        for student in students:
            student.student_id = 'STU-X'
            student.email = 'dup@studysync.ai'
            student.full_name = 'Duplicate Person'
        duplicates = detect_duplicates(students)
        kinds = {item['kind'] for item in duplicates}
        self.assertIn('duplicate_id', kinds)
        self.assertIn('duplicate_email', kinds)
        self.assertIn('duplicate_profile', kinds)

    def test_missing_scores_reports_invalid_values(self):
        student = make_student(1, {'Mathematics': 90, 'Physics': None, 'Programming': 'abc', 'Database': 70, 'Operating Systems': 60})
        missing = missing_scores(student)
        self.assertEqual(missing, ['Physics', 'Programming'])
