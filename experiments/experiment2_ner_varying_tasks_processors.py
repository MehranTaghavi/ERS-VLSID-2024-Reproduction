"""Experiment 2: NER varying tasks and processors."""
import argparse
from pathlib import Path
import sys

# تنظیم مسیر برای دسترسی به ماژول‌های پروژه
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import evaluate
from src.dag_generators import gaussian_elimination
from src.gantt import plot_curve
from src.io_utils import save_rows

def main():
    parser = argparse.ArgumentParser(description="Run Experiment 2: NER vs |V| and |U|")
    parser.add_argument("--trials", type=int, default=250, help="Number of random DAGs per data point")
    parser.add_argument("--ccr", type=float, default=0.5, help="Communication-to-Computation Ratio")
    parser.add_argument("--extension", type=float, default=1.2, help="Deadline extension rate (delta)")
    args = parser.parse_args()

    rows = []
    output_dir = Path(__file__).parent / "output/experiment2_NER_varying_tasks_processors"
    output_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # Experiment 2a: Varying |V| (Tasks)
    # ---------------------------------------------------------
    # مقادیر nu برای گراف Gaussian Elimination به گونه‌ای محاسبه شده‌اند 
    # که دقیقاً تعداد تسک‌های مد نظر مقاله (27 تا 189) را تولید کنند.
    nus = [7, 10, 12, 14, 15, 17, 18, 19]
    task_counts = [27, 54, 77, 104, 119, 152, 170, 189]
    fixed_processors = 8
    ner_vs_tasks = []

    print(f"Running Experiment 2a: Varying |V| (Tasks) with |U|={fixed_processors} ...")
    for nu, v in zip(nus, task_counts):
        scores = []
        for seed in range(args.trials):
            dag = gaussian_elimination(nu, seed, args.ccr)
            _, _, ner = evaluate(dag, fixed_processors, args.extension, seed)
            scores.append(ner)
        
        avg_ner = sum(scores) / len(scores)
        ner_vs_tasks.append(avg_ner)
        rows.append({
            "experiment": "varying_tasks", 
            "tasks_V": v, 
            "processors_U": fixed_processors, 
            "NER": avg_ner
        })
        print(f"  -> |V|={v:3d} : Average NER = {avg_ner:.4f}")

    plot_curve(
        task_counts, 
        ner_vs_tasks, 
        output_dir / "NER_vs_tasks_gaussian.png", 
        "Tasks (|V|)", 
        "Normalized Energy Rate (NER)", 
        "Figure 5(a): NER vs Tasks (Gaussian)"
    )

    # ---------------------------------------------------------
    # Experiment 2b: Varying |U| (Processors)
    # ---------------------------------------------------------
    fixed_nu = 14  # معادل |V| = 104
    processor_counts = [4, 8, 12, 16, 20, 24]
    ner_vs_processors = []

    print(f"\nRunning Experiment 2b: Varying |U| (Processors) with |V|=104 ...")
    for u in processor_counts:
        scores = []
        for seed in range(args.trials):
            dag = gaussian_elimination(fixed_nu, seed, args.ccr)
            _, _, ner = evaluate(dag, u, args.extension, seed)
            scores.append(ner)
            
        avg_ner = sum(scores) / len(scores)
        ner_vs_processors.append(avg_ner)
        rows.append({
            "experiment": "varying_processors", 
            "tasks_V": 104, 
            "processors_U": u, 
            "NER": avg_ner
        })
        print(f"  -> |U|={u:2d} : Average NER = {avg_ner:.4f}")

    plot_curve(
        processor_counts, 
        ner_vs_processors, 
        output_dir / "NER_vs_processors_gaussian.png", 
        "Processors (|U|)", 
        "Normalized Energy Rate (NER)", 
        "Figure 5(b): NER vs Processors (Gaussian)"
    )

    # ---------------------------------------------------------
    # Save Raw Data
    # ---------------------------------------------------------
    save_rows(rows, output_dir / "raw_data.csv")
    print(f"\nExperiment 2 complete! Results and plots are saved to:\n{output_dir}")

if __name__ == "__main__":
    main()