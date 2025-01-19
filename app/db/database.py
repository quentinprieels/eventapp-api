import psycopg2
import csv
from sqlalchemy import create_engine

from app.core.config import settings
from app.db.base import global_engine, GlobalBase, EventBase, GlobalSessionLocal
from app.dependencies import engine_cache, get_minio_db
from app.modules.role.schemas import RoleSchema

# Postgres database
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
    
def load_roles_from_csv(roles_csv_path: str):
    db = GlobalSessionLocal()
    # Check if the roles table is empty
    if db.query(RoleSchema).count():
        return
    
    # Else, load the roles from the CSV file
    with open(roles_csv_path, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            role = RoleSchema(
                id=int(row["id"]),
                categorie=row["categorie"],
                name=row["name"],
                parent_id=row["parent_id"] if row["parent_id"] else None,
                default_global=bool(int(row["default_global"])),
                default_event=bool(int(row["default_event"])),
                default_admin=bool(int(row["default_admin"])),
                description=row["description"],
                access=row["access"]
            )
            db.add(role)
            db.commit()
            db.refresh(role)
    db.close()
    
# Minio database
def init_minio_db():
    minio_db = get_minio_db()
    if not minio_db.bucket_exists(settings.minio_bucket_name):
        minio_db.make_bucket(settings.minio_bucket_name)
