import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# Get all chemicals
print("Fetching chemicals...")
response = requests.get(f"{BASE_URL}/api/chemicals?page_size=100")
chemicals = response.json()['items']
print(f"Found {len(chemicals)} chemicals")

# Select first 3 chemicals for experiment
chem1 = chemicals[0]  # 乙醇
chem2 = chemicals[5]  # 丙酮
chem3 = chemicals[3]  # 甲醇

print(f"\nSelected chemicals:")
print(f"1. {chem1['name']} (CAS: {chem1['cas']})")
print(f"2. {chem2['name']} (CAS: {chem2['cas']})")
print(f"3. {chem3['name']} (CAS: {chem3['cas']})")

# Create Experiment 1
print("\n\nCreating Experiment 1 - 酯化反应实验...")
experiment1_data = {
    "name": "乙酸乙酯合成实验",
    "status": "completed",
    "temperature": 80.0,
    "time": 120,
    "pressure": 1.0,
    "atmosphere": "air",
    "notes": "回流条件下进行酯化反应，观察产物生成情况",
    "reagents": [
        {
            "chemical_id": chem1["id"],  # 乙醇
            "amount_used": 46.07,
            "unit": "g"
        },
        {
            "chemical_id": None,  # 需要乙酸 ID
            "amount_used": 60.05,
            "unit": "g"
        }
    ],
    "result": {
        "yield_percent": 78.5,
        "purity_percent": 95.2,
        "appearance": "无色透明液体，具有水果香味",
        "analysis_data": [
            {
                "type": "NMR",
                "data": "1H NMR (CDCl3): δ 1.26 (t, 3H), 2.04 (s, 3H), 4.12 (q, 2H) ppm"
            },
            {
                "type": "IR",
                "data": "IR (neat): 1740 cm-1 (C=O stretch), 1240 cm-1 (C-O stretch)"
            }
        ],
        "notes": "反应顺利，产率良好。通过蒸馏纯化后得到目标产物。"
    }
}

response = requests.post(f"{BASE_URL}/api/experiments", json=experiment1_data)
if response.status_code == 201:
    exp1 = response.json()
    print(f"✓ Experiment created: {exp1['id']} - {exp1['name']}")
else:
    print(f"✗ Failed to create experiment: {response.text}")

# Create Experiment 2
print("\n\nCreating Experiment 2 - 溶液配制与表征实验...")
experiment2_data = {
    "name": "混合溶剂体系研究",
    "status": "in_progress",
    "temperature": 25.0,
    "time": 60,
    "pressure": 1.0,
    "atmosphere": "air",
    "notes": "研究不同比例溶剂对溶解度的影响",
    "reagents": [
        {
            "chemical_id": chem1["id"],
            "amount_used": 50.0,
            "unit": "ml"
        },
        {
            "chemical_id": chem2["id"],
            "amount_used": 50.0,
            "unit": "ml"
        },
        {
            "chemical_id": chem3["id"],
            "amount_used": 32.04,
            "unit": "ml"
        }
    ],
    "result": {
        "yield_percent": None,
        "purity_percent": None,
        "appearance": "均相透明溶液",
        "analysis_data": [
            {
                "type": "MS",
                "data": "LC-MS: m/z 123.5 [M+H]+, 145.3 [M+Na]+"
            }
        ],
        "notes": "三种溶剂完全互溶，形成稳定均相体系。"
    }
}

response = requests.post(f"{BASE_URL}/api/experiments", json=experiment2_data)
if response.status_code == 201:
    exp2 = response.json()
    print(f"✓ Experiment created: {exp2['id']} - {exp2['name']}")
else:
    print(f"✗ Failed to create experiment: {response.text}")

print("\n\nSample data creation completed!")
print(f"Visit http://localhost:8000/docs to see API documentation")
print(f"Visit http://localhost:5173 to access the frontend application")
