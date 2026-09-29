from fastapi import APIRouter
from pathlib import Path
from fastapi.templating import Jinja2Templates
from fastapi import Request

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]
# WELCOME_HTML = BASE_DIR / "frontend" / "templates" / "welcome.html"

templates = Jinja2Templates(
    directory=BASE_DIR / "frontend" / "templates"
)

@router.get("/welcome/")
async def welcome(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="welcome.html"
    )