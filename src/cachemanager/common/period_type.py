from enum import Enum


class PeriodType(Enum):
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    TTM = 'trailing-months'
    FIRMS = 'firms'
    REGULAR = 'regular'
