class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class InvalidConfigError(Error):
    """Raised when a config file is invalid."""

    pass
