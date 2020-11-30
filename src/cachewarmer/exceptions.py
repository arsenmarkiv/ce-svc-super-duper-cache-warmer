from src.cachewarmer.period_type import PeriodType


class ApiException(Exception):
    def __init__(self, message, status_code=None):
        self.status_code = status_code
        super().__init__(message)


class APIResultException(Exception):
    pass


class NotValidPeriodType(Exception):
    period_types = list(map(str, PeriodType))
    message = f'Not valid period type option. Use one of {period_types} '
