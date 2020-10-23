from cognation.models import Locus
import abc
import re
from collections import OrderedDict


class UnknownFormulaException(Exception):
    def __init__(self, formula_type):
        self.formula_type = formula_type


class LineFormatException(Exception):
    def __str__(self):
        return 'Wrong line format'


class AllelesException(Exception):
    def __str__(self):
        return "Alleles count doesn't look right: "


class UnknownAlleleException(Exception):
    def __init__(self, locus, sat):
        self.locus = locus
        self.sat = sat

    def __str__(self):
        return "Unknown allele found: " + str(self.locus) + " " + str(self.sat)


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
        if len(raw_values) < part_number + 1:
            # Skip line with warning
            raise LineFormatException()

        #  case of 2 participants
        if part_number == 2:
            # child/grandchild for example
            part1_alleles = self.split_sat(raw_values.pop())
            # parent/grandparent...
            part2_alleles = self.split_sat(raw_values.pop())

            locus = ' '.join(raw_values)  # for loci names contain space
            part1_set = set(part1_alleles)  # unique alleles
            part2_set = set(part2_alleles)
            intersection = part1_set & part2_set  # common unique alleles

            if not self.is_gender_specific(locus):
                if len(part1_alleles) != 2 or len(part2_alleles) != 2:
                    raise AllelesException()

            dict_make_result = {'part1': '/'.join(part2_alleles), 'part2': '/'.join(part1_alleles)}

            return part1_alleles, part2_alleles, locus, part1_set, part2_set, intersection, dict_make_result

        #  case of 3 participants
        part3_alleles = self.split_sat(raw_values.pop())
        part2_alleles = self.split_sat(raw_values.pop())
        part1_alleles = self.split_sat(raw_values.pop())
        locus = ' '.join(raw_values)

        if not self.is_gender_specific(locus):
            if len(part1_alleles) != 2 or len(part2_alleles) != 2 or len(part3_alleles) != 2:
                raise AllelesException()

        alleles = [part3_alleles, part2_alleles, part1_alleles]
        sets = [set(part3_alleles), set(part2_alleles), set(part1_alleles)]
        intersections = [sets[2] & sets[1], sets[2] & sets[0], sets[1] & sets[0]]
        dict_make_result = {'part1': '/'.join(part1_alleles), 'part2': '/'.join(part2_alleles), 'part3': '/'.join(part3_alleles)}

        return locus, alleles, sets, intersections, dict_make_result

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
        return re.split(r'/', sat_string)

    @staticmethod
    def make_result(locus, lr, dict_alleles):
        if len(dict_alleles.keys()) == 2:
            return {
                "locus": locus,
                "part1": dict_alleles['part1'],
                "part2": dict_alleles['part2'],
                "lr": lr
            }
        else:
            return {
                "locus": locus,
                "part1": dict_alleles['part1'],
                "part2": dict_alleles['part2'],
                "part3": dict_alleles['part3'],
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
