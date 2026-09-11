"""Evaluation metrics and runtime helpers."""

from time import perf_counter
from typing import Callable
from .models import Schedule


def normalized_energy_rate(esum_max: Schedule, ers_schedule: Schedule) -> float:
    return 0.0 if esum_max.total_energy == 0 else (esum_max.total_energy - ers_schedule.total_energy) / esum_max.total_energy


def measure_runtime(function: Callable[[], object]) -> tuple[object, float]:
    start = perf_counter()
    result = function()
    return result, (perf_counter() - start) * 1000.0