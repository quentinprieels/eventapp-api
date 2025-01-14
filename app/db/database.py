from app.db.base import engine, Base

def init_db():
    Base.metadata.create_all(bind=engine)

def close_db():
    engine.dispose()