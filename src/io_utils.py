import json
from pathlib import Path
import pandas as pd
from .models import DAG

def save_dag_json(dag: DAG, path: str | Path) -> None:
    payload = {
        "tasks": [{"id": task.task_id, "wcet": task.wcet} for task in dag.tasks.values()], 
        "edges": [{"source": edge.source, "target": edge.target, "data": edge.data} for edge in dag.edges]
    }
    
    # اضافه شدن کدهای ساخت پوشه والد
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")

def save_rows(rows: list[dict], path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(destination, index=False)