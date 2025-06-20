from typing import Generator

from app.dbrm import Session, Engine

engine = Engine.from_env()

def get_db() -> Generator:
    with Session(engine) as session:
        yield session