from __future__ import unicode_literals
from .base import Formula
from .base import AllelesException, Calculations


class TwoParentsFormula(Formula):
    def calculate_relation(self, raw_values):
        (locus, alleles, sets, intersections) = self.getting_alleles_locus(raw_values, 3)
        child_alleles, parent1_alleles, parent2_alleles = alleles
        child_set, parent1_set, parent2_set = sets
        intersection1, intersection2 = intersections[0], intersections[1]
        print(locus)
        print('child alleles: ', child_alleles)
        print('parent1 alleles: ', parent1_alleles)
        print('parent2 alleles: ', parent2_alleles)

        if self.is_gender_specific(locus):
            return self.make_result3(locus, '/'.join(child_alleles), '/'.join(parent1_alleles), '/'.join(parent2_alleles), '-')

        if len(child_alleles) != 2 or len(parent1_alleles) != 2 or len(parent2_alleles) != 2:
            raise AllelesException()

        freq_dict = self.get_frequencies(locus, child_alleles + parent1_alleles + parent2_alleles)
        c = Calculations()
        lr = 0

        if len(intersection1) != 0 and len(intersection2) != 0:
            if len(child_set) == 1:
                print('homo')
                print()
                freq = freq_dict[child_alleles[0]]
                lr = (c.F(freq)) ** 2

            else:
                print('hetero')
                print()
                freq1, freq2 = freq_dict[child_alleles[0]], freq_dict[child_alleles[1]]
                lr = 2 * c.F(freq1) * c.F(freq2) - (2 * freq1 * freq2) ** 2

        return self.make_result3(locus, '/'.join(child_alleles), '/'.join(parent1_alleles), '/'.join(parent2_alleles), lr)
