from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from messenger.api import welcome
from messenger.api import chats
from messenger.api import auth
from messenger.api.dependencies import optional_get_current_user
from messenger.database.models import UserORM
from fastapi.responses import RedirectResponse


BASE_DIR = Path(__file__).resolve().parents[2]
static_files = BASE_DIR / "frontend"


app = FastAPI()
app.include_router(welcome.router)
app.include_router(auth.router)
app.include_router(chats.router)
app.mount("/static", StaticFiles(directory=static_files), name="static")

@app.get("/")
async def home(
    user: UserORM | None = Depends(optional_get_current_user)
) -> RedirectResponse:
    if user is None:
        return RedirectResponse("/welcome/", status_code=302)

    return RedirectResponse("/chats/", status_code=302)