class CustomExceptionA(Exception):
    """Срабатывает, когда условие не выполнено (например, неверный флаг)."""

    status_code = 400
    message = "Условие не выполнено: требуется ok=true"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.__class__.message
        super().__init__(self.message)


class CustomExceptionB(Exception):
    """Срабатывает, когда ресурс не найден."""

    status_code = 404
    message = "Ресурс не найден"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.__class__.message
        super().__init__(self.message)
