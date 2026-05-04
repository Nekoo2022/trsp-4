"""Три эндпоинта: регистрация, получение, удаление (задание 11.1)."""

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, EmailStr, Field

from app import in_memory_store as store

router = APIRouter(prefix="/registry", tags=["11.1 in-memory"])


class AccountCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    email: EmailStr


@router.post("/accounts", status_code=201)
def register_account(body: AccountCreate) -> dict[str, int | str]:
    try:
        acc = store.register(body.username, str(body.email))
    except ValueError:
        raise HTTPException(status_code=409, detail="Имя пользователя уже занято")
    return {"id": acc.id, "username": acc.username, "email": acc.email}


@router.get("/accounts/{account_id}")
def get_account(account_id: int) -> dict[str, int | str]:
    acc = store.get_by_id(account_id)
    if acc is None:
        raise HTTPException(status_code=404, detail="Учётная запись не найдена")
    return {"id": acc.id, "username": acc.username, "email": acc.email}


@router.delete("/accounts/{account_id}", status_code=204)
def delete_account(account_id: int) -> Response:
    if not store.delete_by_id(account_id):
        raise HTTPException(status_code=404, detail="Учётная запись не найдена")
    return Response(status_code=204)
