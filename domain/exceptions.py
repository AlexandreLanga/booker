class DomainError(Exception):
    """Base class for domain-level errors."""


class BookNotFoundError(DomainError):
    pass


class InvalidPdfError(DomainError):
    pass


class AnnotationNotFoundError(DomainError):
    pass
