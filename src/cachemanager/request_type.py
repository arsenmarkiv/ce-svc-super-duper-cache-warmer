from enum import Enum


class RequestType(Enum):
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    TTM = 'trailing-months'
    FIRMS = 'firms'
    REGULAR = 'regular'
