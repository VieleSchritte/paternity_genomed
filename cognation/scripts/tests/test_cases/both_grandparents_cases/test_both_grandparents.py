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
            #'hetero_1/both_hetero_ref1',
            #'hetero_2/both_hetero_ref2',
            'homo/homo_ref'
        ]
        self.test_paths = [
            #'hetero_1/both_hetero_test1',
            #'hetero_2/both_hetero_test2',
            'homo/homo_test'
        ]
        short_path = 'cognation/scripts/tests/test_cases/both_grandparents_cases/'
        get_ref = GetData()
        self.overall_ref_dict, self.overall_test_dict = {}, {}

        for i in range(len(self.reference_paths)):
            ref_path, test_path = self.reference_paths[i], self.test_paths[i]
            self.overall_ref_dict[ref_path] = get_ref.get_reference_data(short_path, ref_path)
            self.overall_test_dict[test_path] = get_ref.get_test_data(short_path, test_path, 18)
        pass

    def test_final_assertion(self):
        for i in range(len(self.reference_paths)):
            ref_path, test_path = self.reference_paths[i], self.test_paths[i]
            ref_tuple, test_tuple = self.overall_ref_dict[ref_path], self.overall_test_dict[test_path]
            dict_loci_lrs_ref, dict_loci_lrs_test = ref_tuple[0], test_tuple[0]

            for key in dict_loci_lrs_ref.keys():
                lr_ref, lr_test = dict_loci_lrs_ref[key], dict_loci_lrs_test[key]
                self.assertEqual(lr_ref, lr_test)

            cpi_ref, cpi_test = ref_tuple[1], test_tuple[1]
            p_ref, p_test = int(ref_tuple[2] * 100) / 100, int(test_tuple[2] * 100) / 100
            self.assertEqual(cpi_ref, cpi_test)
            self.assertEqual(p_ref, p_test)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()