"""Experiment 1: NER versus deadline extension."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import evaluate
from src.dag_generators import gaussian_elimination, laplace
from src.gantt import plot_curve
from src.io_utils import save_rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=250)
    parser.add_argument("--processors", type=int, default=8)
    parser.add_argument("--ccr", type=float, default=.5)
    parser.add_argument("--extensions", nargs="+", type=float, default=[1.1, 1.2, 1.3, 1.4, 1.5, 1.6])
    args = parser.parse_args(); rows = []
    for kind in ("gaussian", "laplace"):
        values = []
        for extension in args.extensions:
            scores = []
            for seed in range(args.trials):
                dag = gaussian_elimination(14, seed, args.ccr) if kind == "gaussian" else laplace(10, seed, args.ccr)
                scores.append(evaluate(dag, args.processors, extension, seed)[2])
            average = sum(scores) / len(scores); values.append(average); rows.append({"benchmark": kind, "deadline_extension": extension, "NER": average})
        plot_curve(args.extensions, values, Path(__file__).parent / "output/experiment1_NER_vs_deadline_extension" / f"{kind}_NER_vs_dp.png", "Deadline extension rate", "NER", f"ERS NER: {kind}")
    save_rows(rows, Path(__file__).parent / "output/experiment1_NER_vs_deadline_extension/raw_data.csv")

if __name__ == "__main__": main()