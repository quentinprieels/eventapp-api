import psycopg2
from sqlalchemy import create_engine

from app.core.config import settings
from app.db.base import global_engine, GlobalBase, EventBase
from app.dependencies import engine_cache

def init_global_db():
    GlobalBase.metadata.create_all(bind=global_engine)

def close_all_event_db():
    for engine in engine_cache.values():
        engine.dispose()
        
def close_all_db():
    close_all_event_db()
    global_engine.dispose()

def create_and_init_event_db(event_db_name: str):
    global_db_url = f"{settings.database_url}/{settings.database_name}"
    event_db_url = f"{settings.database_url}/{event_db_name}"
    
    # New database creation
    conn = psycopg2.connect(global_db_url)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE {event_db_name}")
    conn.close()
    
    # New database initialization
    event_engine = create_engine(event_db_url)
    EventBase.metadata.create_all(bind=event_engine)
    event_engine.dispose()
    
def delete_event_db(event_db_name: str):
    global_db_url = f"{settings.database_url}/{settings.database_name}"
    
    # Enshure the database is closed
    if event_db_name in engine_cache:
        engine_cache[event_db_name].dispose()
    
    # Database deletion
    conn = psycopg2.connect(global_db_url)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"DROP DATABASE {event_db_name}")
    conn.close()