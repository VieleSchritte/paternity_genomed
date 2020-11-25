from __future__ import unicode_literals
from .base import Formula


class ParentFormula(Formula):
    def calculate_relation(self, raw_values):
        locus, alleles, sets, intersections, dict_make_result = self.getting_alleles_locus(raw_values, 2)
        parent_set, child_set = sets
        intersection = intersections[0]

        # Function in base.py for checking out if the locus is gender-specific; if yes return lr = '-'
        if self.is_gender_specific(locus):
            return self.make_result(locus, '-', dict_make_result)

        lr = 0
        freq_dict = self.get_frequencies(locus, intersection)
        # i, j     i, j
        if len(freq_dict) == 2:
            divider = 4
            dividend = 0
            for key in freq_dict:
                divider = divider * freq_dict[key]
                dividend = dividend + freq_dict[key]

            if divider != 0:
                # (f1 + f2) / 4 * f1 * f2
                lr = dividend / divider
        elif len(freq_dict) == 1:
            # only 1 allele in common
            # 1 / {1,2}*{1,2}*f
            freq = list(freq_dict.values())[0]
            lr = 1 / (len(parent_set)*len(child_set) * freq)

        return self.make_result(locus, lr, dict_make_result)
