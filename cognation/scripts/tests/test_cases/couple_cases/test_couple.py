# -*- coding: utf-8 -*-
import unittest
from django.test import TestCase
from cognation.scripts.tests import GetData
import logging

logger = logging.getLogger('django.db.backends')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class TestFormula(TestCase):
    def setUp(self):
        self.reference_paths = [
            'no_intersections/no_intersections_ref',
            'aa_an_an/aa_an_an_ref',
            'ab_an_bn/ab_an_bn_ref'
        ]
        self.test_paths = [
            'no_intersections/no_intersections_test',
            'aa_an_an/aa_an_an_test',
            'ab_an_bn/ab_an_bn_test'
        ]

        short_path = 'cognation/scripts/tests/test_cases/couple_cases/'
        get_ref = GetData()
        self.overall_ref_dict = {}
        self.overall_test_dict = {}

        for i in range(len(self.reference_paths)):
            ref_path = self.reference_paths[i]
            self.overall_ref_dict[ref_path] = get_ref.get_reference_data(short_path, ref_path, 3)

            test_path = self.test_paths[i]
            self.overall_test_dict[test_path] = get_ref.get_test_data(short_path, test_path, 7)
        pass

    def test_final_assertion(self):
        for i in range(len(self.reference_paths)):
            ref_path = self.reference_paths[i]
            test_path = self.test_paths[i]

            ref_tuple = self.overall_ref_dict[ref_path]
            test_tuple = self.overall_test_dict[test_path]

            dict_loci_lrs_ref = ref_tuple[0]
            dict_loci_lrs_test = test_tuple[0]

            for key in dict_loci_lrs_ref.keys():
                lr_ref = dict_loci_lrs_ref[key]
                lr_test = dict_loci_lrs_test[key]
                self.assertEqual(lr_ref, lr_test)

            cpi_ref = ref_tuple[1]
            cpi_test = test_tuple[1]
            self.assertEqual(cpi_ref, cpi_test)

            p_ref = int(ref_tuple[2] * 100) / 100
            p_test = int(test_tuple[2] * 100) / 100
            self.assertEqual(p_ref, p_test)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
