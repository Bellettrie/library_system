from django.test import TestCase

from book_code_generation.helpers import normalize_str, normalize_number, standardize_code
from book_code_generation.models import CutterCodeResult, CutterCodeRange
from book_code_generation.procedures.location_number_generation import get_location_number_bounds, \
    get_recommended_result, get_location_numbers, generate_location_number
from creators.models import Creator, CreatorLocationNumber, LocationNumber
from works.models import Location, Category, ItemType


class TestStandardiseCode(TestCase):
    def test_cases(self):
        class TestCase:
            def __init__(self, test_case, expected):
                self.test_case = test_case
                self.expected = expected

        test_cases = {
            TestCase('1','000001'),
            TestCase("SF-T-37-si", "SF-T-37-SI"),
            TestCase("SF-T-370-lr1", "SF-T-37-LR000001"),
            TestCase("SF-S-16-mi399","SF-S-16-MI000399"),
            TestCase("SF-T-370-si", "SF-T-37-SI"),
            TestCase("V-W-11-bo", "N-W-11-BO"),
            TestCase("ASTE 1.7", "ASTE000001.000007"),
            TestCase("SF-T-370-lr1","SF-T-37-LR000001"),
            TestCase("BoB", "BOB"),
            TestCase("Boeken.Zijn.Relaxed", "BOEKEN.ZIJN.RELAXED"),
            TestCase("M-RENO-1", "M-RENO-000001")
        }

        for test_case in test_cases:
            with self.subTest(test_case.test_case):
                res = standardize_code(test_case.test_case)
                self.assertEqual(res, test_case.expected)

class TestLocationNumberGenerationHelpers(TestCase):
    def test_get_location_number_bounds(self):
        cutter_code_results = [CutterCodeResult("Hans Anders", 14),
                               CutterCodeResult("Herman van Veen", 21),
                               CutterCodeResult("Rudolf", 99)]
        s, e = get_location_number_bounds(cutter_code_results, "Abraham")
        self.assertEqual(s, cutter_code_results[0])
        self.assertEqual(e, cutter_code_results[0])

        s, e = get_location_number_bounds(cutter_code_results, normalize_str("Harry"))

        self.assertEqual(s, cutter_code_results[0])
        self.assertEqual(e, cutter_code_results[1])

        s, e = get_location_number_bounds(cutter_code_results, normalize_str("Pingu"))
        self.assertEqual(s, cutter_code_results[1])
        self.assertEqual(e, cutter_code_results[2])

        s, e = get_location_number_bounds(cutter_code_results, normalize_str("Santa"))
        self.assertEqual(s, cutter_code_results[2])
        self.assertEqual(e, cutter_code_results[2])

    def test_get_recommended_result(self):
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        num = get_recommended_result("B", "A", "Z", list(map(normalize_number, numbers)), False)
        self.assertEqual(num, "2")
        num = get_recommended_result("B", "A", "Z", list(map(normalize_number, numbers)), True)
        self.assertEqual(num, "1")
        num = get_recommended_result("P", "A", "Z", list(map(normalize_number, numbers)), False)
        self.assertEqual(num, "6")
        num = get_recommended_result("Y", "A", "Z", list(map(normalize_number, numbers)), False)
        self.assertEqual(num, "9")
        num = get_recommended_result("A", "A", "A", list(map(normalize_number, [1])), False)
        self.assertEqual(num, "1")


class TestLocationNumberGeneration(TestCase):
    def setUp(self):
        CutterCodeRange.objects.create(from_affix="A", to_affix="AAL", number=10, generated_affix="A-10")
        CutterCodeRange.objects.create(from_affix="AAL", to_affix="AAM", number=11, generated_affix="A-11")
        CutterCodeRange.objects.create(from_affix="AAM", to_affix="AAR", number=12, generated_affix="A-12")
        CutterCodeRange.objects.create(from_affix="B", to_affix="BAART", number=10, generated_affix="B-10")
        CutterCodeRange.objects.create(from_affix="BAART", to_affix="BACK", number=11, generated_affix="B-11")
        CutterCodeRange.objects.create(from_affix="BACK", to_affix="BAD", number=12, generated_affix="B-12")
        CutterCodeRange.objects.create(from_affix="BAD", to_affix="BAF", number=13, generated_affix="B-13")
        typ = ItemType.objects.create()
        cat = Category.objects.create(name="A", code="A", item_type=typ)
        self.loc1 = Location.objects.create(name="LOC", old_id=1, category=cat)
        self.loc2 = Location.objects.create(name="LOC2", old_id=2, category=cat)

    def test_get_location_numbers_results_all_cutter_code_range_for__letter(self):
        nums = get_location_numbers(self.loc1, "A", [], [])
        self.assertEqual(len(nums), 4)
        self.assertEqual(nums[0].name, "A")
        self.assertEqual(nums[1].name, "AAL")
        self.assertEqual(nums[2].name, "AAM")
        self.assertEqual(nums[3].name, "AZZZZZZZZZZZZ")
        nums = get_location_numbers(self.loc1, "B", [], [])
        self.assertEqual(len(nums), 5)
        self.assertEqual(nums[0].name, "B")
        self.assertEqual(nums[1].name, "BAART")
        self.assertEqual(nums[2].name, "BACK")
        self.assertEqual(nums[3].name, "BAD")
        self.assertEqual(nums[4].name, "BZZZZZZZZZZZZ")

    def test_get_location_numbers_edge_case_author_removal_out_of_order(self):
        # If a creator gets removed from a location again, then a cutter number from "the book" may become part of the list again.
        # This may, in rare cases, cause the alphabetic order to be disrupted.
        # We expect the system to skip the "book" cutter numbers to prevent alphabetic errors in such cases
        c = Creator.objects.create(name="AALAAF")
        CreatorLocationNumber.objects.create(creator=c, location=self.loc1, number=109, letter="A")
        nums = get_location_numbers(self.loc1, "A", [], [])

        self.assertEqual(len(nums), 4)
        self.assertEqual(nums[0].name, "A")
        self.assertTrue(nums[1].name.startswith("AALAAF"))
        self.assertEqual(nums[2].name, "AAM")
        self.assertEqual(nums[3].name, "AZZZZZZZZZZZZ")

    def test_get_location_numbers_location_codes_override_existing_ones(self):
        c = Creator.objects.create(name="AALBORG")
        CreatorLocationNumber.objects.create(creator=c, location=self.loc1, number=11, letter="A")
        c = Creator.objects.create(name="AANRECHT")
        CreatorLocationNumber.objects.create(creator=c, location=self.loc1, number=12, letter="A")

        nums = get_location_numbers(self.loc1, "A", [], [])
        self.assertEqual(len(nums), 4)
        self.assertEqual(nums[0].name, "A")
        self.assertTrue(nums[1].name.startswith("AALBORG"))
        self.assertTrue(nums[2].name.startswith("AANRECHT"))
        self.assertEqual(nums[3].name, "AZZZZZZZZZZZZ")

    def test_get_location_numbers_location_codes_override_existing_ones_creator_exclude(self):
        c = Creator.objects.create(name="AALBORG")
        CreatorLocationNumber.objects.create(creator=c, location=self.loc1, number=11, letter="A")
        c = Creator.objects.create(name="AANRECHT")
        CreatorLocationNumber.objects.create(creator=c, location=self.loc1, number=12, letter="A")

        nums = get_location_numbers(self.loc1, "A", [c], [])
        self.assertEqual(len(nums), 4)
        self.assertEqual(nums[0].name, "A")
        self.assertTrue(nums[1].name.startswith("AALBORG"))
        self.assertTrue(nums[2].name.startswith("AAM"))
        self.assertEqual(nums[3].name, "AZZZZZZZZZZZZ")

    def test_get_location_numbers_location_codes_override_existing_ones_location_number_exclude(self):
        c = Creator.objects.create(name="AALBORG")
        l1 = CreatorLocationNumber.objects.create(creator=c, location=self.loc1, number=11, letter="A")
        c = Creator.objects.create(name="AANRECHT")
        l2 = CreatorLocationNumber.objects.create(creator=c, location=self.loc1, number=12, letter="A")

        nums = get_location_numbers(self.loc1, "A", [], [l1.pk, l2.pk])
        self.assertEqual(len(nums), 4)
        self.assertEqual(nums[0].name, "A")
        self.assertTrue(nums[1].name.startswith("AAL"))
        self.assertTrue(nums[2].name.startswith("AAM"))
        self.assertEqual(nums[3].name, "AZZZZZZZZZZZZ")

    def test_generate_location_number_recommends_boundary_if_still_default(self):
        let, lowest, recommended, highest = generate_location_number("AALBORG", self.loc1)
        self.assertEqual(let, "A")
        self.assertEqual(lowest, "11")
        self.assertEqual(recommended, "11")
        self.assertEqual(highest, "119")

    def test_generate_location_number_recommends_above_boundary_if_boundary_already_location_specific(self):
        c = Creator.objects.create(name="AALBORG")
        CreatorLocationNumber.objects.create(creator=c, location=self.loc1, number=11, letter="A")
        let, lowest, recommended, highest = generate_location_number("AALBORGG", self.loc1)
        self.assertEqual(let, "A")
        self.assertEqual(lowest, "111")
        # Note the 112, because we don't accept 1-ending ones by default
        self.assertEqual(recommended, "112")
        self.assertEqual(highest, "119")

        let, lowest, recommended, highest = generate_location_number("AALBORGG", self.loc1, also_keep_first_result=True)
        self.assertEqual(let, "A")
        self.assertEqual(lowest, "111")
        # Note the 112, because we don't accept 1-ending ones by default
        self.assertEqual(recommended, "111")
        self.assertEqual(highest, "119")
