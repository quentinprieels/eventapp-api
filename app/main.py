import logging
import time
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import RedirectResponse

from app.db.database import init_global_db, close_global_db, init_minio_db, load_roles_from_csv
from app.modules.user.router import router as user_router
from app.modules.event.router import router as event_router
from app.core.config import settings
from app.helpers.logs import StructuredLogger

from app.modules.event.schemas import *

# Logging configuration
logging.setLoggerClass(StructuredLogger)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler(settings.log_file, maxBytes=settings.log_max_size, backupCount=settings.log_backup_count)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Lifespan events
async def lifespan(app: FastAPI):
    init_global_db()
    init_minio_db()
    with open("app.log", "w"):  # Clear the log file
        pass
    load_roles_from_csv()
    yield
    close_global_db()

# FastAPI application
app = FastAPI(lifespan=lifespan,
              title=settings.app_name,
              version=settings.app_version,
              root_path="/api/v1")

##############
# MIDDLEWARE #
##############
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    background_tasks = BackgroundTasks()
    background_tasks.add_task(
        logger.info, 
        {
            "event": "request",
            "method": request.method, 
            "url": str(request.url), 
            "headers": dict(request.headers), 
            "client": request.client.host, 
            "response_code": response.status_code,
            "process_time": process_time # in seconds
        }
    )
    response.background = background_tasks
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
app.include_router(event_router)
