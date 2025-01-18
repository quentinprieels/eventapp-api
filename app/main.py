import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import RedirectResponse

from app.db.database import init_global_db, close_all_db
from app.modules.user.router import router as user_router
from app.core.config import settings
from app.helpers.logs import StructuredLogger

# Logging configuration
logging.setLoggerClass(StructuredLogger)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler(settings.log_file, maxBytes=settings.log_max_size, backupCount=settings.log_backup_count)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Lifespan events
async def lifespan(app: FastAPI):
    init_global_db()
    with open("app.log", "w"):  # Clear the log file
        pass
    yield
    close_all_db()

# FastAPI application
app = FastAPI(lifespan=lifespan)

##############
# MIDDLEWARE #
##############
@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    background_tasks = BackgroundTasks()
    background_tasks.add_task(logger.info, {"event": "request", "method": request.method, "url": str(request.url), "headers": dict(request.headers), "client": request.client.host, "response_code": response.status_code})
    return response

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
