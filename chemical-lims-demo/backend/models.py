from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./lims.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 化学品模型
class Chemical(Base):
    __tablename__ = "chemicals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    cas = Column(String(50), unique=True, index=True, nullable=False)
    molecular_formula = Column(String(100))
    molecular_weight = Column(Float)
    hazard_class = Column(String(50))  # 易燃，易爆，腐蚀性等
    storage_conditions = Column(String(200))
    stock_quantity = Column(Float, default=0)

    experiments = relationship("ExperimentReagent", back_populates="chemical", cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 实验模型
class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    status = Column(String(20), default="in_progress")  # in_progress, completed, failed
    temperature = Column(Float)
    time = Column(Integer)  # 分钟
    pressure = Column(Float)
    atmosphere = Column(String(50))  # air, nitrogen, argon, vacuum
    notes = Column(Text)

    reagents = relationship("ExperimentReagent", back_populates="experiment", cascade="all, delete-orphan")
    result = relationship("ExperimentResult", back_populates="experiment", uselist=False, cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 实验 - 试剂关联表（多对多）
class ExperimentReagent(Base):
    __tablename__ = "experiment_reagents"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    chemical_id = Column(Integer, ForeignKey("chemicals.id"), nullable=False)
    amount_used = Column(Float, nullable=False)
    unit = Column(String(10), default="g")  # g, ml, mmol

    experiment = relationship("Experiment", back_populates="reagents")
    chemical = relationship("Chemical", back_populates="experiments")

# 实验结果模型
class ExperimentResult(Base):
    __tablename__ = "experiment_results"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), unique=True, nullable=False)
    
    yield_percent = Column(Float)  # 产率
    purity_percent = Column(Float)  # 纯度
    appearance = Column(String(200))  # 外观描述
    
    analysis_data = Column(JSON)  # 分析数据 [{type: 'NMR', data: '...'}, ...]
    notes = Column(Text)  # 实验笔记

    experiment = relationship("Experiment", back_populates="result")

# 创建数据库表
def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully!")
