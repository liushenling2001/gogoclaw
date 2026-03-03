"""初始化示例数据"""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import Base, engine, Chemical
from sqlalchemy.orm import Session

def init_sample_data():
    """创建示例化学品数据"""
    
    # 检查是否已有数据
    with Session(engine) as session:
        count = session.query(Chemical).count()
        if count > 0:
            print(f"数据库中已有 {count} 条化学品数据，跳过初始化")
            return
        
        # 定义示例化学品
        sample_chemicals = [
            {
                "name": "乙醇",
                "cas": "64-17-5",
                "molecular_formula": "C2H6O",
                "molecular_weight": 46.07,
                "hazard_class": "易燃",
                "storage_conditions": "密封、避光、阴凉处",
                "stock_quantity": 1000.0
            },
            {
                "name": "乙酸乙酯",
                "cas": "141-78-6",
                "molecular_formula": "C4H8O2",
                "molecular_weight": 88.11,
                "hazard_class": "易燃",
                "storage_conditions": "密封、避光、阴凉处",
                "stock_quantity": 500.0
            },
            {
                "name": "二氯甲烷",
                "cas": "75-09-2",
                "molecular_formula": "CH2Cl2",
                "molecular_weight": 84.93,
                "hazard_class": "毒性",
                "storage_conditions": "密封、避光、通风橱内",
                "stock_quantity": 800.0
            },
            {
                "name": "甲醇",
                "cas": "67-56-1",
                "molecular_formula": "CH4O",
                "molecular_weight": 32.04,
                "hazard_class": "易燃",
                "storage_conditions": "密封、避光、阴凉处",
                "stock_quantity": 600.0
            },
            {
                "name": "正己烷",
                "cas": "110-54-3",
                "molecular_formula": "C6H14",
                "molecular_weight": 86.18,
                "hazard_class": "易燃",
                "storage_conditions": "密封、避光、阴凉处",
                "stock_quantity": 400.0
            },
            {
                "name": "丙酮",
                "cas": "67-64-1",
                "molecular_formula": "C3H6O",
                "molecular_weight": 58.08,
                "hazard_class": "易燃",
                "storage_conditions": "密封、避光、阴凉处",
                "stock_quantity": 750.0
            },
            {
                "name": "硫酸",
                "cas": "7664-93-9",
                "molecular_formula": "H2SO4",
                "molecular_weight": 98.08,
                "hazard_class": "腐蚀性",
                "storage_conditions": "密封、耐腐蚀容器",
                "stock_quantity": 2000.0
            },
            {
                "name": "氢氧化钠",
                "cas": "1310-73-2",
                "molecular_formula": "NaOH",
                "molecular_weight": 40.00,
                "hazard_class": "腐蚀性",
                "storage_conditions": "密封、干燥处",
                "stock_quantity": 1500.0
            }
        ]
        
        for chem_data in sample_chemicals:
            chem = Chemical(**chem_data)
            session.add(chem)
        
        session.commit()
        print(f"成功添加了 {len(sample_chemicals)} 个示例化学品!")
        print("\n示例化学品列表:")
        for chem in session.query(Chemical).all():
            print(f"  - {chem.name} (CAS: {chem.cas})")

if __name__ == "__main__":
    print("开始初始化示例数据...")
    init_sample_data()
