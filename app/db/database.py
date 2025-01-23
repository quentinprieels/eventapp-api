import csv

from app.core.config import settings
from app.db.base import global_engine, GlobalBase, GlobalSessionLocal
from app.dependencies import get_minio_db
from app.modules.role.schemas import GlobalRoleSchema, EventRoleSchema


# Postgres database connection
def init_global_db():
    GlobalBase.metadata.create_all(bind=global_engine)


def close_global_db():
    global_engine.dispose()


# Load roles from CSV
def _load_roles_from_csv(role_schema, roles_csv_path):
    db = GlobalSessionLocal()
    # Check if the roles table is empty
    if db.query(role_schema).count() > 0:
        return

    # Else, load the roles from the CSV file
    with open(roles_csv_path, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            role = role_schema(
                name=str(row["name"]),
                parent_name=str(row["parent_name"]) if row["parent_name"] else None,
                is_default=bool(int(row["is_default"])),
                is_admin=bool(int(row["is_admin"])),
                description=str(row["description"]),
                access=str(row["access"]),
            )
            db.add(role)
            db.commit()
            db.refresh(role)
    db.close()


def load_roles_from_csv():
    _load_roles_from_csv(GlobalRoleSchema, settings.global_roles_csv_path)
    _load_roles_from_csv(EventRoleSchema, settings.event_roles_csv_path)


# Minio database
def init_minio_db():
    minio_db = get_minio_db()
    if not minio_db.bucket_exists(settings.minio_bucket_name):
        minio_db.make_bucket(settings.minio_bucket_name)
