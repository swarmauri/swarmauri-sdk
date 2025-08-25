from fastapi import APIRouter

router = APIRouter()

from . import register, login, logout  # noqa: E402,F401
