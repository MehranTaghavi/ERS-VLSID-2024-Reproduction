"""Equations 1-8 from the implementation specification."""

from typing import Mapping
from .models import DAG, Platform, Schedule


def execution_time(wcet: float, frequency: float, platform: Platform) -> float:
    if frequency <= 0:
        raise ValueError("Frequency must be positive")
    return wcet * platform.fmax / frequency


def power(platform: Platform, frequency: float, active: int = 1) -> float:
    return platform.ps + active * (platform.pind + platform.capacitance * frequency ** platform.exponent)


def dynamic_task_energy(wcet: float, frequency: float, platform: Platform) -> float:
    return (platform.pind + platform.capacitance * frequency ** platform.exponent) * execution_time(wcet, frequency, platform)


def communication_time(platform: Platform, source_processor: int, target_processor: int, data: float) -> float:
    return 0.0 if source_processor == target_processor else data / platform.transfer_rate(source_processor, target_processor)


def communication_energy(dag: DAG, platform: Platform, task_id: str, mapping: Mapping[str, int]) -> float:
    data = dag.edge_data
    return platform.ecr * sum(
        communication_time(platform, mapping[source], mapping[task_id], data[(source, task_id)])
        for source in dag.predecessors[task_id]
    )


def energy_breakdown(dag: DAG, platform: Platform, schedule: Schedule) -> tuple[float, float, float]:
    dynamic = sum(
        dynamic_task_energy(dag.tasks[task].wcet, placement.frequency, platform)
        + communication_energy(dag, platform, task, schedule.mapping)
        for task, placement in schedule.placements.items()
    )
    static = platform.processor_count * platform.ps * schedule.makespan
    return static, dynamic, static + dynamic


def total_energy(dag: DAG, platform: Platform, schedule: Schedule) -> float:
    return energy_breakdown(dag, platform, schedule)[2]