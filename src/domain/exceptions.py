"""Domain-specific exceptions"""


class DomainError(Exception):
    """Base exception for all domain errors"""

    pass


class ConfigurationError(DomainError):
    """Raised when there's a configuration problem"""

    pass


class ValidationError(DomainError):
    """Raised when domain validation fails"""

    pass


class DataQualityError(DomainError):
    """Raised when data quality issues are detected"""

    pass


class InsufficientDataError(DomainError):
    """Raised when there's not enough data for analysis"""

    pass


class ProcessingError(DomainError):
    """Raised when processing fails"""

    pass
