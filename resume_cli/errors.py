class AppError(Exception):
    """An expected, user-facing application error."""

    def __init__(
        self, code: str, message: str, *, cause: Exception | None = None
    ) -> None:
        super().__init__(message)
        self.code = code
        self.cause = cause


def to_user_error(error: Exception) -> AppError:
    if isinstance(error, AppError):
        return error
    return AppError("UNEXPECTED_ERROR", str(error) or "发生了未知错误。", cause=error)
