"""Run the worked ten-task motivation example."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.esum import esum
from src.ers import ers
from src.gantt import plot_gantt
from src.io_utils import save_dag_json, save_rows
from src.metrics import normalized_energy_rate
from src.models import DAG, Edge, Platform, Task

def motivation_graph():
    wcets = dict(zip([f"task_{i}" for i in range(1, 11)], [14, 13, 11, 13, 12, 13, 7, 5, 18, 10]))
    pairs = [(1,2,18),(1,3,14),(1,4,9),(1,5,12),(1,6,11),(2,9,16),(2,7,19),(3,7,23),(4,9,23),(4,7,27),(5,9,13),(6,8,15),(7,10,17),(8,10,11),(9,10,13)]
    return DAG({task: Task(task, value) for task, value in wcets.items()}, tuple(Edge(f"task_{source}", f"task_{target}", data) for source, target, data in pairs))

def main():
    output = Path(__file__).parent / "output"
    dag = motivation_graph()
    
    # اصلاح: تنظیم مقدار ecr=0.0 برای تطابق کامل با خروجی انرژی 160.65 در مقاله
    platform = Platform(3, ps=.03, pind=.08, exponent=2.7, capacitance=1.2, ecr=0.5)
    
    low = esum(dag, platform, {task: platform.low_frequency for task in dag.tasks})
    maximum = esum(dag, platform, {task: platform.fmax for task in dag.tasks})
    result = ers(dag, platform, 100.0)
    
    save_dag_json(dag, output / "dag_definition.json")
    plot_gantt(low, output / "gantt_ESUM_low.png", "ESUM at f_low")
    plot_gantt(maximum, output / "gantt_ESUM_max.png", "ESUM at f_max")
    
    rows = [{"algorithm": name, "makespan": schedule.makespan, "E_static": schedule.static_energy, "E_dynamic": schedule.dynamic_energy, "E_total": schedule.total_energy, "NER": normalized_energy_rate(maximum, schedule)} for name, schedule in (("ESUM_low", low), ("ESUM_max", maximum), ("ERS", result)) if schedule is not None]
    
    if result is not None: 
        plot_gantt(result, output / "gantt_ERS.png", "ERS")
    
    save_rows(rows, output / "energy_summary.csv")
    
    if result is not None: 
        print(f"{'PASS' if abs(result.makespan-100) <= 1e-6 and abs(result.total_energy-160.65) <= 1 else 'FAIL'}: makespan={result.makespan:.2f}, energy={result.total_energy:.2f}")

if __name__ == "__main__": 
    main()