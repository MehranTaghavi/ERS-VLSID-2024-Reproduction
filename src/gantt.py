"""Matplotlib visualizations for schedules and experiment results."""

from pathlib import Path
import matplotlib.pyplot as plt
from .models import Schedule


def plot_gantt(schedule: Schedule, output: str | Path, title: str) -> None:
    processors = sorted({placement.processor for placement in schedule.placements.values()})
    figure, axis = plt.subplots(figsize=(10, 4))
    for placement in schedule.placements.values():
        axis.barh(placement.processor, placement.finish - placement.start, left=placement.start, height=0.6)
        axis.text((placement.start + placement.finish) / 2, placement.processor, placement.task_id, ha="center", va="center", fontsize=8)
    axis.set_yticks(processors, [f"u{processor + 1}" for processor in processors])
    axis.set_xlabel("Time (ms)")
    axis.set_title(title)
    axis.grid(axis="x", alpha=0.25)
    figure.tight_layout()
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=180)
    plt.close(figure)


def plot_curve(x_values, y_values, output: str | Path, xlabel: str, ylabel: str, title: str) -> None:
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.plot(x_values, y_values, marker="o")
    axis.set(xlabel=xlabel, ylabel=ylabel, title=title)
    axis.grid(alpha=0.25)
    figure.tight_layout()
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=180)
    plt.close(figure)