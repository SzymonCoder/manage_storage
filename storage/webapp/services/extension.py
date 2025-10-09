class ServiceException(Exception):
    pass

class NotFoundDataException(ServiceException):
    pass


class ValidationException(ServiceException):
    pass



#tutaj mozna dac rozne Exception dizedziczas juz po class ServiceException
# przyklad z innego projektu:

# class InsufficientStockException(ServiceException):
#     pass