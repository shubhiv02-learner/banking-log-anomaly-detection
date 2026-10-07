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


SALVERIS_RATE_LIMIT_DETAIL = "Salveris rate limit reached. Try again in a moment."


class SalverisRateLimitError(SalverisError):
    """Salveris rejected the call because of a rate limit."""

    def __init__(
        self,
        message: str = SALVERIS_RATE_LIMIT_DETAIL,
        *,
        status_code: int | None = 429,
    ):
        super().__init__(message, status_code=status_code)
