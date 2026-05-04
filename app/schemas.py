from typing import Optional

from pydantic import BaseModel, EmailStr, Field, conint, constr


class ErrorResponse(BaseModel):
    """Единый формат тела ответа при ошибках (задание 10.1)."""

    detail: str = Field(..., description="Сообщение об ошибке")
    error_code: str = Field(..., description="Внутренний код ошибки")


class CheckQuery(BaseModel):
    ok: bool = Field(False, description="Если true — условие выполнено")


class User(BaseModel):
    """Модель пользователя для валидации JSON (задание 10.2)."""

    username: str
    age: conint(gt=18)  # type: ignore[valid-type]
    email: EmailStr
    password: constr(min_length=8, max_length=16)  # type: ignore[valid-type]
    phone: Optional[str] = "Unknown"


class ValidationErrorResponse(BaseModel):
    """Ответ при ошибке проверки тела запроса (кастомный 422)."""

    detail: str = Field(..., description="Общее описание ошибки")
    error_code: str = Field(default="VALIDATION_ERROR")
    issues: list[str] = Field(
        default_factory=list,
        description="Список сообщений по полям",
    )
