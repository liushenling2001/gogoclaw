from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from math import ceil

from models import Chemical, Experiment, ExperimentReagent, ExperimentResult, Base, engine
from schemas import (
    ChemicalCreate, ChemicalUpdate, ChemicalResponse,
    ExperimentCreate, ExperimentUpdate, ExperimentDetailResponse, ExperimentListResponse,
    ResultCreate, ResultUpdate, ResultResponse,
    ReagentUse, AnalysisData
)
from database import get_db

app = FastAPI(
    title="LIMS Lite API",
    description="实验室信息管理系统 - 简化版",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建数据库表（开发环境）
Base.metadata.create_all(bind=engine)

# ==================== 化学品 API ====================

@app.get("/api/chemicals")
def list_chemicals(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """获取化学品列表（支持分页和搜索）"""
    query = db.query(Chemical)
    
    if keyword:
        query = query.filter(
            (Chemical.name.ilike(f"%{keyword}%")) | 
            (Chemical.cas.ilike(f"%{keyword}%"))
        )
    
    total = query.count()
    pages = ceil(total / page_size) if total > 0 else 1
    
    chemicals = query.order_by(Chemical.id.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()
    
    # Convert SQLAlchemy objects to dicts
    chemical_list = []
    for chem in chemicals:
        chemical_list.append({
            "id": chem.id,
            "name": chem.name,
            "cas": chem.cas,
            "molecular_formula": chem.molecular_formula,
            "molecular_weight": chem.molecular_weight,
            "hazard_class": chem.hazard_class,
            "storage_conditions": chem.storage_conditions,
            "stock_quantity": chem.stock_quantity,
            "created_at": chem.created_at.isoformat(),
            "updated_at": chem.updated_at.isoformat()
        })
    
    return {
        "items": chemical_list,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": pages
        }
    }

@app.post("/api/chemicals", response_model=ChemicalResponse, status_code=status.HTTP_201_CREATED)
def create_chemical(chemical: ChemicalCreate, db: Session = Depends(get_db)):
    """新增化学品"""
    # 检查 CAS 号是否已存在
    existing = db.query(Chemical).filter(Chemical.cas == chemical.cas).first()
    if existing:
        raise HTTPException(status_code=400, detail="CAS 号已存在")
    
    db_chemical = Chemical(**chemical.model_dump())
    db.add(db_chemical)
    db.commit()
    db.refresh(db_chemical)
    return db_chemical

@app.get("/api/chemicals/{chemical_id}", response_model=ChemicalResponse)
def get_chemical(chemical_id: int, db: Session = Depends(get_db)):
    """获取单个化学品详情"""
    chemical = db.query(Chemical).filter(Chemical.id == chemical_id).first()
    if not chemical:
        raise HTTPException(status_code=404, detail="化学品不存在")
    return chemical

@app.put("/api/chemicals/{chemical_id}", response_model=ChemicalResponse)
def update_chemical(chemical_id: int, chemical: ChemicalUpdate, db: Session = Depends(get_db)):
    """更新化学品信息"""
    db_chemical = db.query(Chemical).filter(Chemical.id == chemical_id).first()
    if not db_chemical:
        raise HTTPException(status_code=404, detail="化学品不存在")
    
    update_data = chemical.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_chemical, field, value)
    
    db.commit()
    db.refresh(db_chemical)
    return db_chemical

@app.delete("/api/chemicals/{chemical_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chemical(chemical_id: int, db: Session = Depends(get_db)):
    """删除化学品"""
    db_chemical = db.query(Chemical).filter(Chemical.id == chemical_id).first()
    if not db_chemical:
        raise HTTPException(status_code=404, detail="化学品不存在")
    
    db.delete(db_chemical)
    db.commit()
    return None

# ==================== 实验 API ====================

@app.get("/api/experiments", response_model=dict)
def list_experiments(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[str] = Query(None, description="状态过滤"),
    db: Session = Depends(get_db)
):
    """获取实验列表（支持分页、搜索和状态过滤）"""
    query = db.query(Experiment)
    
    if keyword:
        query = query.filter(
            (Experiment.name.ilike(f"%{keyword}%")) | 
            (Experiment.notes.ilike(f"%{keyword}%"))
        )
    
    if status:
        query = query.filter(Experiment.status == status)
    
    total = query.count()
    pages = ceil(total / page_size) if total > 0 else 1
    
    experiments = query.order_by(Experiment.id.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()
    
    items = []
    for exp in experiments:
        reagent_count = db.query(ExperimentReagent).filter(ExperimentReagent.experiment_id == exp.id).count()
        result = db.query(ExperimentResult).filter(ExperimentResult.experiment_id == exp.id).first()
        
        items.append({
            "id": exp.id,
            "name": exp.name,
            "status": exp.status,
            "temperature": exp.temperature,
            "time": exp.time,
            "pressure": exp.pressure,
            "atmosphere": exp.atmosphere,
            "notes": exp.notes,
            "reagent_count": reagent_count,
            "created_at": exp.created_at,
            "updated_at": exp.updated_at,
            "result": {
                "yield_percent": result.yield_percent if result else None,
                "purity_percent": result.purity_percent if result else None,
                "appearance": result.appearance if result else None
            } if result else None
        })
    
    return {
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": pages
        }
    }

@app.post("/api/experiments", response_model=ExperimentDetailResponse, status_code=status.HTTP_201_CREATED)
def create_experiment(experiment: ExperimentCreate, db: Session = Depends(get_db)):
    """新建实验"""
    # 验证试剂是否存在
    for reagent in experiment.reagents:
        chem = db.query(Chemical).filter(Chemical.id == reagent.chemical_id).first()
        if not chem:
            raise HTTPException(status_code=400, detail=f"化学品 ID {reagent.chemical_id} 不存在")
    
    # 创建实验记录
    db_experiment = Experiment(**experiment.model_dump(exclude=["reagents", "result"]))
    db.add(db_experiment)
    db.flush()
    
    # 添加试剂关联
    for reagent in experiment.reagents:
        exp_reagent = ExperimentReagent(
            experiment_id=db_experiment.id,
            chemical_id=reagent.chemical_id,
            amount_used=reagent.amount_used,
            unit=reagent.unit
        )
        db.add(exp_reagent)
    
    db.commit()
    db.refresh(db_experiment)
    
    # 如果有结果数据，一并创建
    if experiment.result:
        db_result = ExperimentResult(
            experiment_id=db_experiment.id,
            yield_percent=experiment.result.yield_percent,
            purity_percent=experiment.result.purity_percent,
            appearance=experiment.result.appearance,
            analysis_data=[r.model_dump() for r in experiment.result.analysis_data],
            notes=experiment.result.notes
        )
        db.add(db_result)
        db.commit()
    
    # 返回完整详情
    return get_experiment_detail(db_experiment.id, db)

@app.get("/api/experiments/{experiment_id}", response_model=ExperimentDetailResponse)
def get_experiment(experiment_id: int, db: Session = Depends(get_db)):
    """获取单个实验详情"""
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="实验不存在")
    
    return get_experiment_detail(experiment_id, db)

def get_experiment_detail(experiment_id: int, db: Session):
    """获取实验详情的辅助函数"""
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    
    # 获取试剂列表
    reagents = db.query(ExperimentReagent).filter(ExperimentReagent.experiment_id == experiment_id).all()
    reagent_list = []
    for r in reagents:
        chem = db.query(Chemical).filter(Chemical.id == r.chemical_id).first()
        reagent_list.append({
            "id": r.id,
            "chemical_id": r.chemical_id,
            "chemical_name": chem.name if chem else f"ID: {r.chemical_id}",
            "amount_used": r.amount_used,
            "unit": r.unit
        })
    
    # 获取结果
    result = db.query(ExperimentResult).filter(ExperimentResult.experiment_id == experiment_id).first()
    result_data = None
    if result:
        result_data = ResultResponse(
            id=result.id,
            experiment_id=result.experiment_id,
            yield_percent=result.yield_percent,
            purity_percent=result.purity_percent,
            appearance=result.appearance,
            analysis_data=result.analysis_data,
            notes=result.notes,
            created_at=result.created_at,
            updated_at=result.updated_at
        )
    
    return {
        "id": experiment.id,
        "name": experiment.name,
        "status": experiment.status,
        "temperature": experiment.temperature,
        "time": experiment.time,
        "pressure": experiment.pressure,
        "atmosphere": experiment.atmosphere,
        "notes": experiment.notes,
        "reagents": reagent_list,
        "result": result_data,
        "created_at": experiment.created_at,
        "updated_at": experiment.updated_at
    }

@app.put("/api/experiments/{experiment_id}", response_model=ExperimentDetailResponse)
def update_experiment(experiment_id: int, experiment: ExperimentUpdate, db: Session = Depends(get_db)):
    """更新实验信息"""
    db_experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not db_experiment:
        raise HTTPException(status_code=404, detail="实验不存在")
    
    # 更新基本信息
    update_data = experiment.model_dump(exclude_unset=True, exclude=["reagents", "result"])
    for field, value in update_data.items():
        setattr(db_experiment, field, value)
    
    # 更新试剂列表
    if experiment.reagents is not None:
        # 删除旧的试剂关联
        db.query(ExperimentReagent).filter(ExperimentReagent.experiment_id == experiment_id).delete()
        
        # 添加新的试剂关联
        for reagent in experiment.reagents:
            exp_reagent = ExperimentReagent(
                experiment_id=experiment_id,
                chemical_id=reagent.chemical_id,
                amount_used=reagent.amount_used,
                unit=reagent.unit
            )
            db.add(exp_reagent)
    
    # 更新或创建结果
    if experiment.result is not None:
        db_result = db.query(ExperimentResult).filter(ExperimentResult.experiment_id == experiment_id).first()
        if db_result:
            # 更新现有结果
            update_data = experiment.result.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if field == "analysis_data" and value:
                    setattr(db_result, field, [AnalysisData(**item).model_dump() for item in value])
                else:
                    setattr(db_result, field, value)
        else:
            # 创建新结果
            new_result = ExperimentResult(
                experiment_id=experiment_id,
                **experiment.result.model_dump(exclude_unset=True)
            )
            if new_result.analysis_data:
                new_result.analysis_data = [AnalysisData(**item).model_dump() for item in new_result.analysis_data]
            db.add(new_result)
    
    db.commit()
    db.refresh(db_experiment)
    
    return get_experiment_detail(experiment_id, db)

@app.delete("/api/experiments/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experiment(experiment_id: int, db: Session = Depends(get_db)):
    """删除实验"""
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="实验不存在")
    
    # 级联删除已通过 relationship cascade 设置
    db.delete(experiment)
    db.commit()
    return None

@app.post("/api/experiments/{experiment_id}/results", response_model=ResultResponse)
def create_experiment_result(
    experiment_id: int,
    result: ResultCreate,
    db: Session = Depends(get_db)
):
    """为实验创建结果"""
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="实验不存在")
    
    db_result = ExperimentResult(
        experiment_id=experiment_id,
        yield_percent=result.yield_percent,
        purity_percent=result.purity_percent,
        appearance=result.appearance,
        analysis_data=[item.model_dump() for item in result.analysis_data],
        notes=result.notes
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    return ResultResponse(**db_result.__dict__)

@app.patch("/api/experiments/{experiment_id}/results", response_model=ResultResponse)
def update_experiment_result(
    experiment_id: int,
    result: ResultUpdate,
    db: Session = Depends(get_db)
):
    """更新实验结果"""
    db_result = db.query(ExperimentResult).filter(ExperimentResult.experiment_id == experiment_id).first()
    if not db_result:
        raise HTTPException(status_code=404, detail="实验结果不存在")
    
    update_data = result.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "analysis_data" and value:
            setattr(db_result, field, [AnalysisData(**item).model_dump() for item in value])
        else:
            setattr(db_result, field, value)
    
    db.commit()
    db.refresh(db_result)
    
    return ResultResponse(**db_result.__dict__)

# ==================== 健康检查 ====================

@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok"}
