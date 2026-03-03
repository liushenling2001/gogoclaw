from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

# 化学品相关
class ChemicalBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="化学品名称")
    cas: str = Field(..., min_length=1, max_length=50, description="CAS 号")
    molecular_formula: Optional[str] = Field(None, max_length=100, description="分子式")
    molecular_weight: Optional[float] = Field(None, description="分子量")
    hazard_class: Optional[str] = Field(None, description="危险品分类")
    storage_conditions: Optional[str] = Field(None, max_length=200, description="存储条件")
    stock_quantity: Optional[float] = Field(0, description="库存量 (g)")

class ChemicalCreate(ChemicalBase):
    pass

class ChemicalUpdate(ChemicalBase):
    pass

class ChemicalResponse(ChemicalBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 试剂使用（实验中的化学品）
class ReagentUse(BaseModel):
    chemical_id: int = Field(..., description="化学品 ID")
    amount_used: float = Field(..., gt=0, description="使用量")
    unit: str = Field("g", description="单位：g, ml, mmol")

# 分析数据
class AnalysisData(BaseModel):
    type: str = Field(..., description="分析类型：NMR, IR, MS, HPLC 等")
    data: str = Field(..., description="分析数据")

# 实验结果
class ResultBase(BaseModel):
    yield_percent: Optional[float] = Field(None, ge=0, le=100, description="产率%")
    purity_percent: Optional[float] = Field(None, ge=0, le=100, description="纯度%")
    appearance: Optional[str] = Field(None, max_length=200, description="外观描述")
    analysis_data: Optional[List[AnalysisData]] = Field(default_factory=list, description="分析数据")
    notes: Optional[str] = Field(None, description="实验笔记")

class ResultCreate(ResultBase):
    pass

class ResultUpdate(ResultBase):
    pass

class ResultResponse(ResultBase):
    id: int
    experiment_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 实验相关
class ExperimentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="实验名称")
    status: str = Field("in_progress", description="实验状态：in_progress, completed, failed")
    temperature: Optional[float] = Field(None, description="温度 (°C)")
    time: Optional[int] = Field(None, ge=0, description="时间 (分钟)")
    pressure: Optional[float] = Field(None, description="压力 (atm)")
    atmosphere: Optional[str] = Field(None, description="气氛")
    notes: Optional[str] = Field(None, description="备注")

class ExperimentCreate(ExperimentBase):
    reagents: List[ReagentUse] = Field(default_factory=list, description="使用的试剂列表")
    result: Optional[ResultCreate] = Field(None, description="实验结果")

class ExperimentUpdate(ExperimentBase):
    reagents: Optional[List[ReagentUse]] = None
    result: Optional[ResultUpdate] = None

class ExperimentDetailResponse(ExperimentBase):
    id: int
    reagents: List[dict]
    result: Optional[ResultResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ExperimentListResponse(ExperimentBase):
    id: int
    reagent_count: int
    created_at: datetime

    class Config:
        from_attributes = True

# 分页响应
class PaginationInfo(BaseModel):
    page: int
    page_size: int
    total: int
    pages: int

class PaginatedResponse(BaseModel):
    items: List[Any]
    pagination: PaginationInfo
