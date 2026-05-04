from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app.exceptions import CustomExceptionA, CustomExceptionB
from app.registry_router import router as registry_router
from app.schemas import ErrorResponse, User, ValidationErrorResponse

app = FastAPI(title="TRSP: задания 9.1–11.1")
app.include_router(registry_router)


def _format_validation_issues(exc: RequestValidationError) -> list[str]:
    lines: list[str] = []
    for err in exc.errors():
        loc_parts = [str(p) for p in err.get("loc", ()) if p != "body"]
        loc = ".".join(loc_parts) if loc_parts else "request"
        msg = err.get("msg", "ошибка проверки")
        lines.append(f"{loc}: {msg}")
    return lines


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    print(f"[RequestValidationError] {exc.errors()}")
    body = ValidationErrorResponse(
        detail="Неверные данные запроса",
        error_code="VALIDATION_ERROR",
        issues=_format_validation_issues(exc),
    ).model_dump()
    return JSONResponse(status_code=422, content=body)


@app.exception_handler(CustomExceptionA)
async def handle_custom_a(_: Request, exc: CustomExceptionA) -> JSONResponse:
    print(f"[CustomExceptionA] {exc.message}")
    body = ErrorResponse(detail=exc.message, error_code="CUSTOM_A").model_dump()
    return JSONResponse(status_code=exc.status_code, content=body)


@app.exception_handler(CustomExceptionB)
async def handle_custom_b(_: Request, exc: CustomExceptionB) -> JSONResponse:
    print(f"[CustomExceptionB] {exc.message}")
    body = ErrorResponse(detail=exc.message, error_code="CUSTOM_B").model_dump()
    return JSONResponse(status_code=exc.status_code, content=body)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/users", status_code=201)
def create_user(user: User) -> dict[str, str | int | None]:
    """Принимает JSON пользователя; тело проверяется моделью User (задание 10.2)."""
    return {
        "status": "created",
        "username": user.username,
        "age": user.age,
        "email": str(user.email),
        "phone": user.phone,
    }


@app.get("/check-condition")
def check_condition(ok: bool = False) -> dict[str, str]:
    """Если ok не true — выбрасывается CustomExceptionA (HTTP 400)."""
    if not ok:
        raise CustomExceptionA()
    return {"result": "условие выполнено"}


@app.get("/items/{item_id}")
def get_item(item_id: int) -> dict[str, int]:
    """Несуществующий id — CustomExceptionB (HTTP 404)."""
    if item_id < 1:
        raise CustomExceptionB("Некорректный идентификатор")
    if item_id > 999:
        raise CustomExceptionB(f"Элемент с id={item_id} не найден")
    return {"item_id": item_id}


@app.get("/products/schema-check")
def products_schema_check(db: Session = Depends(get_db)) -> dict[str, list[str] | bool]:
    """Проверка, что в таблице products есть колонка description (после второй миграции)."""
    _ = db  # зависимость открывает сессию; схему читаем через engine
    insp = inspect(engine)
    columns = [c["name"] for c in insp.get_columns("products")]
    return {"columns": columns, "has_description": "description" in columns}


@app.on_event("startup")
def startup() -> None:
    """Проверка соединения с БД при старте (миграции должны быть уже применены)."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


# Удобная точка входа: uvicorn app.main:app --reload
