import unittest
from django.test import TestCase
from cognation.scripts.tests import GetData
# import logging
# logger = logging.getLogger('django.db.backends')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())


class TestFormula(TestCase):
    def setUp(self):
        self.reference_paths = [
            'no_intersections/no_intersections_ref',
            'aa_an_an/aa_an_an_ref',
            'ab_an_bn/ab_an_bn_ref',
            'ab_ab_an/ab_ab_an_ref',
            'ab_ab_bn/ab_ab_bn_ref'
        ]
        self.test_paths = [
            'no_intersections/no_intersections_test',
            'aa_an_an/aa_an_an_test',
            'ab_an_bn/ab_an_bn_test',
            'ab_ab_an/ab_ab_an_test',
            'ab_ab_bn/ab_ab_bn_test'
        ]

        short_path = 'cognation/scripts/tests/test_cases/one_known_supposed_cases/'
        get_ref = GetData()
        self.overall_ref_dict, self.overall_test_dict = {}, {}

        for i in range(len(self.reference_paths)):
            ref_path, test_path = self.reference_paths[i], self.test_paths[i]
            self.overall_ref_dict[ref_path] = get_ref.get_reference_data(short_path, ref_path)
            self.overall_test_dict[test_path] = get_ref.get_test_data(short_path, test_path, 8)

    def test_formula(self):
        for i in range(len(self.reference_paths)):
            ref_path, test_path = self.reference_paths[i], self.test_paths[i]
            ref_tuple, test_tuple = self.overall_ref_dict[ref_path], self.overall_test_dict[test_path]
            dict_loci_lrs_ref, dict_loci_lrs_test = ref_tuple[0], test_tuple[0]

            for key in dict_loci_lrs_ref.keys():
                lr_ref, lr_test = dict_loci_lrs_ref[key], dict_loci_lrs_test[key]
                self.assertEqual(lr_ref, lr_test, key)

            cpi_ref, cpi_test = ref_tuple[1], test_tuple[1]
            p_ref, p_test = float(ref_tuple[2]), float(test_tuple[2])
            self.assertEqual(cpi_ref, cpi_test)
            self.assertEqual(p_ref, p_test)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()