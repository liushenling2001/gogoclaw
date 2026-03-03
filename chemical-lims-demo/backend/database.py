from sqlalchemy.orm import Session
from models import create_tables, SessionLocal

# 创建数据库表
create_tables()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
