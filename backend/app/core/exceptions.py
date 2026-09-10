class DomainError(Exception):
    """Base class for business errors raised by services.

    The message carries the French label shown to the user; the class itself is
    what `app.main` maps to an HTTP status code.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    """A requested resource does not exist."""


class AlreadyExistsError(DomainError):
    """A resource with the same unique key already exists."""


class BusinessRuleError(DomainError):
    """A business invariant would be violated."""


class InsufficientStockError(DomainError):
    """The requested quantity exceeds available stock."""
