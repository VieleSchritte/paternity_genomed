from cognation.formulas.parent import ParentFormula
from cognation.formulas.grandparent import GrandParentFormula
from cognation.formulas.uncle import UncleFormula
from cognation.formulas.cousin import CousinFormula
from cognation.formulas.stepbrother import StepbrotherFormula
from cognation.formulas.brother import BrotherFormula
from cognation.formulas.sibling import SiblingFormula
from cognation.formulas.couple import CoupleFormula
from cognation.formulas.base import UnknownFormulaException
from cognation.formulas.two_children import TwoChildrenFormula
from cognation.formulas.three_children import ThreeChildrenFormula
from cognation.formulas.grand_parent_yes import YesGrandParent
from cognation.formulas.one_known_supposed import OneKnownSupposedFormula
from cognation.formulas.two_known_supposed import TwoKnownSupposedFormula
from cognation.formulas.two_brothers import TwoBrothersFormula
from cognation.formulas.three_known_supposed import ThreeKnownSupposed
from cognation.formulas.two_couple import TwoCoupleFormula
from cognation.formulas.three_couple import ThreeCoupleFormula
from cognation.formulas.no_both_grands_parent import NoBothGrandsParent
from cognation.formulas.grand_parent_no import NoGrandParent
from cognation.formulas.both_grandparents import BothGrandparents
from cognation.formulas.IBD_grandparent import IBDGrandParent
from cognation.formulas.known_supposed_grand import GrandKnownSupposed


numToFormula = {
    1: ParentFormula,
    2: TwoChildrenFormula,
    3: SiblingFormula,
    4: ThreeChildrenFormula,
    5: TwoKnownSupposedFormula,
    6: ThreeKnownSupposed,
    7: CoupleFormula,
    8: OneKnownSupposedFormula,
    9: TwoCoupleFormula,
    10: ThreeCoupleFormula,
    11: StepbrotherFormula,
    12: BrotherFormula,
    13: TwoBrothersFormula,
    14: CousinFormula,
    15: UncleFormula,
    16: NoBothGrandsParent,
    17: GrandParentFormula,
    18: BothGrandparents,
    19: YesGrandParent,
    20: NoGrandParent,
    21: IBDGrandParent,
    22: GrandKnownSupposed
}


def formula_builder(data_type, participants_data):
    normalized_type = int(data_type)
    if normalized_type in numToFormula.keys():
        return numToFormula[normalized_type](participants_data)
    else:
        raise UnknownFormulaException(data_type)
