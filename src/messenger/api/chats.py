from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from messenger.api.dependencies import get_current_user
from messenger.database.models import UserORM
from fastapi import Depends
from pathlib import Path


router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]

templates = Jinja2Templates(
    directory=BASE_DIR / "frontend" / "templates"
)

@router.get("/chats/")
async def chats(
    request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="chats.html"
    )

@router.get("/api/chats/", status_code=200)
async def api_chats(
    current_user: UserORM = Depends(get_current_user)
):
    return {
        "message": "ok"
    }