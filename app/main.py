from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.db.database import init_global_db, close_all_db
from app.modules.user.router import router as user_router
from app.core.config import settings

async def lifespan(app: FastAPI):
    init_global_db()
    yield
    close_all_db()

app = FastAPI(lifespan=lifespan)

##########
# ROUTES #
##########
@app.get("/")
def redirect_to_website():
    """"Redirect to the 'settings.website_url'."""
    return RedirectResponse(url=settings.website_url)

###################
# INCLUDE ROUTERS #
###################
app.include_router(user_router)
