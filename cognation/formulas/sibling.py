from __future__ import unicode_literals
from cognation.formulas.base import Formula, Calculations


class SiblingFormula(Formula):
    def calculate_relation(self, raw_values):
        locus, alleles, sets, intersections, dict_make_result = self.getting_alleles_locus(raw_values, 3)
        sibling_alleles, parent_alleles, child_alleles = alleles
        sibling_set, parent_set, child_set = sets
        cp_intersection, sc_intersection, sp_intersection = intersections

        # Function in base.py for checking out if the locus is gender-specific; if yes return lr = '-'
        if self.is_gender_specific(locus):
            return self.make_result(locus, '-', dict_make_result)

        #  If there's no relation then return lr = 0 and start collecting mutations
        if len(sp_intersection) == 0 or len(cp_intersection) == 0:
            lr = 0
            return self.make_result(locus, lr, dict_make_result)

        c = Calculations()
        freq_dict = self.get_frequencies(locus, child_alleles + parent_alleles + sibling_alleles)
        unavailable_parent_alleles = [0, 0]

        # Homozygous child
        if len(child_set) == 1:
            freq = freq_dict[child_alleles[0]]
            refutation = c.homo_refutation(freq)

            #  A special case for confirmation = F(Pa) / (F(Pa) + F(Pb) - 2 * Pa * Pb) aa ab ab
            if len(parent_set) == 2 and parent_set == sibling_set:
                freq2 = freq_dict[self.get_unique_allele(parent_alleles, child_alleles)]
                confirmation = c.F(freq) / (c.F(freq) + c.F(freq2) - 2 * freq * freq2)
                lr = confirmation / refutation
                return self.make_result(locus, lr, dict_make_result)

        # Heterozygous child
        else:
            freq1, freq2 = freq_dict[child_alleles[0]], freq_dict[child_alleles[1]]
            refutation = c.hetero_refutation(freq1, freq2)

            # A special case for confirmation = M(Pc, Pa) + M(Pc, Pb) ab ab ac
            if parent_set == child_set and len(sibling_set) == 2 and sibling_set != parent_set:
                freq1, freq2 = freq_dict[parent_alleles[0]], freq_dict[parent_alleles[1]]
                freq3 = freq_dict[self.get_unique_allele(sibling_alleles, parent_alleles)]
                confirmation = c.M(freq3, freq1) + c.M(freq3, freq2)
                lr = confirmation / refutation
                return self.make_result(locus, lr, dict_make_result)

            #  A special case for confirmation = 2 * Pb / (2 - Pa - Pc) ab ac ac
            if parent_set == sibling_set and parent_set != child_set and len(parent_set) == len(sibling_set) == 2:
                freq1, freq3 = freq_dict[parent_alleles[0]], freq_dict[parent_alleles[1]]
                freq2 = freq_dict[self.get_unique_allele(child_alleles, parent_alleles)]
                confirmation = 2 * freq2 / (2 - freq1 - freq3)
                lr = confirmation / refutation
                return self.make_result(locus, lr, dict_make_result)

            # ab aa ac case confirmation = M(Pc, Pa)
            if len(child_set) == len(sibling_set) == 2 and child_set != sibling_set and len(parent_set) == 1:
                unavailable_parent_alleles = self.get_parent2_alleles(unavailable_parent_alleles, sibling_alleles, sp_intersection, 0)
                unavailable_parent_alleles[1] = list(sp_intersection)[0]
                lr = self.get_lr(freq_dict, unavailable_parent_alleles, refutation)
                return self.make_result(locus, lr, dict_make_result)

            # ab ac aa case confirmation = M(Pa, Pc)
            if len(child_set) == len(parent_set) == 2 and len(sibling_set) == len(sp_intersection) == len(cp_intersection) == len(sc_intersection) == 1 and child_set != parent_set:
                unavailable_parent_alleles[1] = self.get_unique_allele(parent_alleles, child_alleles)
                unavailable_parent_alleles = self.get_parent2_alleles(unavailable_parent_alleles, sibling_alleles, sp_intersection, 0)
                lr = self.get_lr(freq_dict, unavailable_parent_alleles, refutation)
                return self.make_result(locus, lr, dict_make_result)

        # Default is confirmation = M(x,y); x, y = unavailable_parent_alleles[0], unavailable_parent_alleles[1]
        unavailable_parent_alleles = self.get_parent2_alleles(unavailable_parent_alleles, sibling_alleles, sp_intersection, 0)
        unavailable_parent_alleles = self.get_parent2_alleles(unavailable_parent_alleles, child_alleles, cp_intersection, 1)
        set_unavailable = set(unavailable_parent_alleles)

        # special case for confirmation = 1
        if len(set_unavailable) == 1:
            lr = 1 / refutation
            return self.make_result(locus, lr, dict_make_result)

        lr = self.get_lr(freq_dict, unavailable_parent_alleles, refutation)
        return self.make_result(locus, lr, dict_make_result)

    # A method to fill M(freq1, freq2) formula in base.Calculations. Returns list of alleles in required range
    @staticmethod
    def get_parent2_alleles(parent2_alleles, ch_sib_alleles, intersection, position):
        counter = 0

        for allele in ch_sib_alleles:
            if allele == list(intersection)[0]:
                counter += 1

        if counter == 2:
            parent2_alleles[position] = ch_sib_alleles[position]
        else:
            for allele in ch_sib_alleles:
                if allele == list(intersection)[0]:
                    continue
                else:
                    parent2_alleles[position] = allele

        return parent2_alleles

    # A method to get unique allele from list1 (list2 doesn't include this allele)
    @staticmethod
    def get_unique_allele(list1, list2):
        for allele in list1:
            if allele not in list2:
                return allele

    @staticmethod
    def get_lr(freq_dict, parent2_alleles, refutation):
        c = Calculations()
        freq1, freq2 = freq_dict[parent2_alleles[0]], freq_dict[parent2_alleles[1]]
        confirmation = c.M(freq1, freq2)
        lr = confirmation / refutation
        return lr
