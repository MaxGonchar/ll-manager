class InvalidPostUserExpressionDataException(Exception):
    def __init__(
        self,
        message: str,
    ) -> None:
        super().__init__(message)


class UserNotFoundException(Exception):
    pass


class TagNotFoundException(Exception):
    pass


class UserExpressionNotFoundException(Exception):
    pass


class PasswordDoesntMatchException(Exception):
    pass


class ExpressionNotFoundException(Exception):
    pass


class InvalidUpdateExpressionDataException(Exception):
    pass
