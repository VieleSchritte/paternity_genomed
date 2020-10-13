from cognation.models import Locus
import abc
import re
from collections import Counter
from collections import OrderedDict


# Exception - if something isn't right in data format
class UnknownFormulaException(Exception):
    def __init__(self, formula_type):
        self.formula_type = formula_type


class LineFormatException(Exception):
    def __str__(self):
        return 'Wrong line format'


class AllelesException(Exception):
    def __str__(self):
        return "Alleles count doesn't look right"


class UnknownAlleleException(Exception):
    def __init__(self, locus, sat):
        self.locus = locus
        self.sat = sat

    def __str__(self):
        return "Unknown allele found: " + str(self.sat)


# Abstract parent class
class Formula(abc.ABC):
    def __init__(self, user_data):
        self.user_data = str(user_data)

    # Checking out if the locus is gender-specific (so we don't need to add it to cpi calculation)
    @staticmethod
    def is_gender_specific(locus):
        gender_specific_loci = ['SRY', 'DYS391', 'Yindel']
        for i in range(len(gender_specific_loci)):
            if locus == gender_specific_loci[i]:
                return True
        return False

    def getting_alleles_locus(self, raw_values, part_number):
        #  case of 2 participants
        if part_number == 2:
            if len(raw_values) < 3:
                # Skip line with warning
                raise LineFormatException()

            # child/grandchild for example
            part1_alleles = self.split_sat(raw_values.pop())
            # parent/grandparent...
            part2_alleles = self.split_sat(raw_values.pop())

            locus = ' '.join(raw_values)  # for loci names contain space
            part1_set = set(part1_alleles)  # unique alleles
            part2_set = set(part2_alleles)
            intersection = part1_set & part2_set  # common unique alleles

            return part1_alleles, part2_alleles, locus, part1_set, part2_set, intersection

        #  case of 3 participants
        if len(raw_values) < 4:
            # Skip line with warning
            raise LineFormatException()

        part3_alleles = self.split_sat(raw_values.pop())
        part2_alleles = self.split_sat(raw_values.pop())
        part1_alleles = self.split_sat(raw_values.pop())
        alleles = [part3_alleles, part2_alleles, part1_alleles]
        locus = ' '.join(raw_values)

        part3_set = set(part3_alleles)
        part2_set = set(part2_alleles)
        part1_set = set(part1_alleles)
        sets = [part3_set, part2_set, part1_set]

        intersection12 = part1_set & part2_set
        intersection13 = part1_set & part3_set
        intersection23 = part2_set & part3_set
        intersections = [intersection12, intersection13, intersection23]

        return locus, alleles, sets, intersections

    def calculate(self):
        result = OrderedDict()
        lines = self.user_data.splitlines()
        for line in lines:
            line = line.strip(' \t\n\r')
            if len(line) == 0:
                continue

            try:
                relation = self.calculate_relation(re.split(r'[\s\t]+', line))
                result[relation['locus']] = relation
            except (LineFormatException, AllelesException, UnknownAlleleException) as exception:
                result[hash(line)] = {'exception': exception, 'line': line}
        return result

    # getting allele frequencies from DB
    def get_frequencies(self, locus, sat_set):
        result = {}
        for sat in sat_set:
            try:
                locus_object = Locus.objects.get(locus=locus, sat=self.normalize_sat(sat))
                result[sat] = locus_object.freq
            except Locus.DoesNotExist:
                raise UnknownAlleleException(locus, sat)

        return result

    def get_template(self):
        return 'cognation/formula/' + self.__class__.__name__.lower()[:-7] + '.html'

    @staticmethod
    def normalize_sat(value):
        if value == 'X':
            return 0.0
        elif value == 'Y':
            return 1.0
        else:
            return float(value)

    @staticmethod
    def split_sat(sat_string):
        return re.split(r'\/', sat_string)

    @staticmethod
    def make_result(locus, ab, cd, lr):
        return {
            "locus": locus,
            "ab": ab,
            "cd": cd,
            "lr": lr
        }

    @staticmethod
    def get_sat_counter(sat_string):
        return Counter(Formula.split_sat(sat_string))

    @staticmethod
    def make_result2(locus, part1, part2, lr):
        return {
            "locus": locus,
            "part1": part1,
            "part2": part2,
            "lr": lr
        }

    @staticmethod
    def make_result3(locus, part1, part2, part3, lr):
        return {
            "locus": locus,
            "part1": part1,
            "part2": part2,
            "part3": part3,
            "lr": lr
        }

    # Abstract methods
    @abc.abstractmethod
    def calculate_relation(self, row_values):
        """ Abstract method to calculate """


# Calculation Helpers
class Calculations:
    #  A helper for the frequently used pattern F(Px) = Px * (2 - Px)
    @staticmethod
    def F(freq):
        return freq * (2 - freq)

    #  A helper for the frequently used pattern Q(Px) = 0.5 - 0.5 * Px (for GrandParentFormula)
    @staticmethod
    def Q(freq):
        return 0.5 + 0.5 * freq

    #  A helper for the frequently used pattern M(Px, Py) = 2 * Px * Py / F(Px) (for SiblingFormula)
    def M(self, freq1, freq2):
        return 2 * freq1 * freq2 / self.F(freq1)

    #  Probability of relation theory refutation in case of inspected person's homozygosity
    def homo_refutation(self, freq):
        return (self.F(freq)) ** 2

    #  Probability of relation theory refutation in case of inspected person's heterozygosity
    def hetero_refutation(self, freq1, freq2):
        return 2 * self.F(freq1) * self.F(freq2) - (2 * freq1 * freq2) ** 2

    
