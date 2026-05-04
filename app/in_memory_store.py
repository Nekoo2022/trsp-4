"""Простое in-memory хранилище учётных записей (задание 11.1)."""

from __future__ import annotations

from dataclasses import dataclass

_accounts: dict[int, dict[str, str]] = {}
_username_to_id: dict[str, int] = {}
_next_id: int = 1


@dataclass(frozen=True)
class Account:
    id: int
    username: str
    email: str


def clear_registry() -> None:
    """Очистка хранилища (для тестов и сброса демо-состояния)."""
    global _next_id
    _accounts.clear()
    _username_to_id.clear()
    _next_id = 1


def register(username: str, email: str) -> Account:
    if username in _username_to_id:
        raise ValueError("username_taken")
    global _next_id
    uid = _next_id
    _next_id += 1
    row = {"username": username, "email": email}
    _accounts[uid] = row
    _username_to_id[username] = uid
    return Account(id=uid, username=username, email=email)


def get_by_id(uid: int) -> Account | None:
    row = _accounts.get(uid)
    if row is None:
        return None
    return Account(id=uid, username=row["username"], email=row["email"])


def delete_by_id(uid: int) -> bool:
    row = _accounts.pop(uid, None)
    if row is None:
        return False
    _username_to_id.pop(row["username"], None)
    return True
