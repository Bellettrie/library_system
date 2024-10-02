from django.test import TestCase

from book_code_generation.models import CutterCodeResult, CutterCodeRange
from book_code_generation.procedures.location_number_generation import get_location_number_bounds, \
    get_recommended_result, get_location_numbers
from creators.models import Creator, CreatorLocationNumber, LocationNumber
from works.models import Location, Category, ItemType


class TestLocationNumberGenerationHelpers(TestCase):
    def test_get_location_number_bounds(self):
        cutter_code_results = [CutterCodeResult("Hans Anders", 14),
                               CutterCodeResult("Herman van Veen", 21),
                               CutterCodeResult("Rudolf", 99)]
        s, e = get_location_number_bounds(cutter_code_results, "Abraham")
        self.assertEqual(s, cutter_code_results[0])
        self.assertEqual(e, cutter_code_results[0])

        s, e = get_location_number_bounds(cutter_code_results, "Harry")
        self.assertEqual(s, cutter_code_results[0])
        self.assertEqual(e, cutter_code_results[1])

        s, e = get_location_number_bounds(cutter_code_results, "Pingu")
        self.assertEqual(s, cutter_code_results[1])
        self.assertEqual(e, cutter_code_results[2])

        s, e = get_location_number_bounds(cutter_code_results, "Santa")
        self.assertEqual(s, cutter_code_results[2])
        self.assertEqual(e, cutter_code_results[2])

    def test_get_recommended_result(self):
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        num = get_recommended_result("B", "A", "Z", numbers, False)
        self.assertEqual(num, 2)
        num = get_recommended_result("B", "A", "Z", numbers, True)
        self.assertEqual(num, 1)
        num = get_recommended_result("P", "A", "Z", numbers, False)
        self.assertEqual(num, 6)
        num = get_recommended_result("Y", "A", "Z", numbers, False)
        self.assertEqual(num, 9)
        num = get_recommended_result("A", "A", "A", [1], False)
        self.assertEqual(num, 1)


class TestLocationNumberGeneration(TestCase):
    l = None
    l2 = None

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
        TestLocationNumberGeneration.l = Location.objects.create(name="LOC", old_id=1, category=cat)
        TestLocationNumberGeneration.l2 = Location.objects.create(name="LOC2", old_id=2, category=cat)

    def test_get_location_numbers_results_all_cutter_code_range_for__letter(self):
        nums = get_location_numbers(TestLocationNumberGeneration.l, "A", [], [])
        self.assertEqual(len(nums), 4)
        self.assertEqual(nums[0].name, "A")
        self.assertEqual(nums[1].name, "AAL")
        self.assertEqual(nums[2].name, "AAM")
        self.assertEqual(nums[3].name, "AZZZZZZZZZZZZ")
        nums = get_location_numbers(TestLocationNumberGeneration.l, "B", [], [])
        self.assertEqual(len(nums), 5)
        self.assertEqual(nums[0].name, "B")
        self.assertEqual(nums[1].name, "BAART")
        self.assertEqual(nums[2].name, "BACK")
        self.assertEqual(nums[3].name, "BAD")
        self.assertEqual(nums[4].name, "BZZZZZZZZZZZZ")

    def test_get_location_numbers_location_codes_override_existing_ones(self):
        c = Creator.objects.create(name="AALBORG")
        CreatorLocationNumber.objects.create(creator=c, location=TestLocationNumberGeneration.l, number=11, letter="A")
        c = Creator.objects.create(name="AANRECHT")
        CreatorLocationNumber.objects.create(creator=c, location=TestLocationNumberGeneration.l, number=12, letter="A")

        nums = get_location_numbers(TestLocationNumberGeneration.l, "A", [], [])
        self.assertEqual(len(nums), 4)
        self.assertEqual(nums[0].name, "A")
        self.assertTrue(nums[1].name.startswith("AALBORG"))
        self.assertTrue(nums[2].name.startswith("AANRECHT"))
        self.assertEqual(nums[3].name, "AZZZZZZZZZZZZ")


def test_get_location_numbers_location_codes_override_existing_ones_creator_exclude(self):
    c = Creator.objects.create(name="AALBORG")
    CreatorLocationNumber.objects.create(creator=c, location=TestLocationNumberGeneration.l, number=11, letter="A")
    c = Creator.objects.create(name="AANRECHT")
    CreatorLocationNumber.objects.create(creator=c, location=TestLocationNumberGeneration.l, number=12, letter="A")

    nums = get_location_numbers(TestLocationNumberGeneration.l, "A", [c], [])
    self.assertEqual(len(nums), 4)
    self.assertEqual(nums[0].name, "A")
    self.assertTrue(nums[1].name.startswith("AALBORG"))
    self.assertTrue(nums[2].name.startswith("AAM"))
    self.assertEqual(nums[3].name, "AZZZZZZZZZZZZ")


def test_get_location_numbers_location_codes_override_existing_ones_location_number_exclude(self):
    c = Creator.objects.create(name="AALBORG")
    CreatorLocationNumber.objects.create(creator=c, location=TestLocationNumberGeneration.l, number=11, letter="A")
    c = Creator.objects.create(name="AANRECHT")
    CreatorLocationNumber.objects.create(creator=c, location=TestLocationNumberGeneration.l, number=12, letter="A")

    nums = get_location_numbers(TestLocationNumberGeneration.l, "A", [], [l1.pk, l2.pk])
    self.assertEqual(len(nums), 4)
    self.assertEqual(nums[0].name, "A")
    self.assertTrue(nums[1].name.startswith("AAL"))
    self.assertTrue(nums[2].name.startswith("AAM"))
    self.assertEqual(nums[3].name, "AZZZZZZZZZZZZ")
