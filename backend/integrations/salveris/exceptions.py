"""Exceptions for Salveris HTTP integration."""


class SalverisError(Exception):
    """Base Salveris integration error."""

    def __init__(self, message: str, *, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class SalverisAuthError(SalverisError):
    """Authentication / authorization failure talking to Salveris."""


class SalverisUnavailable(SalverisError):
    """Salveris unreachable or timed out."""


class SalverisConfigError(SalverisError):
    """Missing or invalid Salveris configuration."""
