"""Data models for DAGs, uniform platforms, and static schedules."""

from dataclasses import dataclass, field
from typing import Dict, Mapping, Tuple


@dataclass(frozen=True)
class Task:
    task_id: str
    wcet: float


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    data: float


@dataclass(frozen=True)
class DAG:
    tasks: Mapping[str, Task]
    edges: Tuple[Edge, ...]

    def __post_init__(self) -> None:
        ids = set(self.tasks)
        if any(edge.source not in ids or edge.target not in ids for edge in self.edges):
            raise ValueError("Every edge endpoint must be a task")
        if self._has_cycle():
            raise ValueError("DAG contains a cycle")

    @property
    def task_ids(self) -> Tuple[str, ...]:
        return tuple(self.tasks)

    @property
    def predecessors(self) -> Dict[str, Tuple[str, ...]]:
        result = {task: [] for task in self.tasks}
        for edge in self.edges:
            result[edge.target].append(edge.source)
        return {task: tuple(values) for task, values in result.items()}

    @property
    def successors(self) -> Dict[str, Tuple[str, ...]]:
        result = {task: [] for task in self.tasks}
        for edge in self.edges:
            result[edge.source].append(edge.target)
        return {task: tuple(values) for task, values in result.items()}

    @property
    def edge_data(self) -> Dict[Tuple[str, str], float]:
        return {(edge.source, edge.target): edge.data for edge in self.edges}

    @property
    def entry(self) -> str:
        entries = [task for task, values in self.predecessors.items() if not values]
        if len(entries) != 1:
            raise ValueError("DAG must have one entry task")
        return entries[0]

    @property
    def exit(self) -> str:
        exits = [task for task, values in self.successors.items() if not values]
        if len(exits) != 1:
            raise ValueError("DAG must have one exit task")
        return exits[0]

    def _has_cycle(self) -> bool:
        state = {task: 0 for task in self.tasks}
        successors = {task: [] for task in self.tasks}
        for edge in self.edges:
            successors[edge.source].append(edge.target)

        def visit(task: str) -> bool:
            if state[task] == 1:
                return True
            if state[task] == 2:
                return False
            state[task] = 1
            if any(visit(child) for child in successors[task]):
                return True
            state[task] = 2
            return False

        return any(visit(task) for task in self.tasks)


@dataclass(frozen=True)
class Platform:
    processor_count: int
    transfer_rates: Mapping[Tuple[int, int], float] = field(default_factory=dict)
    ps: float = 0.03
    pind: float = 0.08
    exponent: float = 2.7
    capacitance: float = 1.2
    ecr: float = 0.5
    fmin: float = 0.1
    fmax: float = 1.0
    frequency_step: float = 0.1

    def __post_init__(self) -> None:
        if self.processor_count < 1 or self.fmin <= 0 or self.fmax < self.fmin:
            raise ValueError("Invalid platform configuration")
        if self.pind < 0 or self.ps < 0 or self.exponent <= 1 or self.capacitance <= 0:
            raise ValueError("Invalid power parameters")

    def transfer_rate(self, source: int, target: int) -> float:
        if source == target:
            return float("inf")
        rate = self.transfer_rates.get((source, target), 1.0)
        if rate <= 0:
            raise ValueError("Transfer rates must be positive")
        return rate

    @property
    def frequencies(self) -> Tuple[float, ...]:
        count = round((self.fmax - self.fmin) / self.frequency_step)
        return tuple(round(self.fmin + index * self.frequency_step, 10) for index in range(count + 1))

    @property
    def critical_frequency(self) -> float:
        return (self.pind / ((self.exponent - 1) * self.capacitance)) ** (1 / self.exponent)

    @property
    def low_frequency(self) -> float:
        requested = max(self.fmin, self.critical_frequency)
        return min(self.fmax, min(self.frequencies, key=lambda value: (abs(value - requested), value)))


@dataclass(frozen=True)
class Placement:
    task_id: str
    processor: int
    frequency: float
    start: float
    finish: float


@dataclass(frozen=True)
class Schedule:
    placements: Mapping[str, Placement]
    ranks: Mapping[str, float]
    makespan: float
    static_energy: float
    dynamic_energy: float
    total_energy: float
    frequencies: Mapping[str, float]

    @property
    def mapping(self) -> Dict[str, int]:
        return {task: placement.processor for task, placement in self.placements.items()}