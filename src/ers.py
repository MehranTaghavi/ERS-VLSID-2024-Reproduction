"""ERS deadline phase and its two heap implementation."""

import heapq
from typing import List
from .esum import esum
from .models import DAG, Platform, Schedule


def benefit_to_cost(current: Schedule, candidate: Schedule, delta: float = 0.01) -> float:
    return (candidate.total_energy - current.total_energy + delta) / (current.makespan - candidate.makespan + delta)


def ers(dag: DAG, platform: Platform, deadline: float) -> Schedule | None:
    frequencies = {task: platform.low_frequency for task in dag.tasks}
    current = esum(dag, platform, frequencies)
    min_heap: List[tuple[float, int, str, float]] = []
    max_heap: List[tuple[float, int, str, float]] = []
    serial = 0

    def probe(task_id: str) -> None:
        nonlocal serial
        frequency = frequencies[task_id]
        if frequency >= platform.fmax - 1e-9:
            return
        target = round(frequency + platform.frequency_step, 10)
        trial_frequencies = dict(frequencies)
        trial_frequencies[task_id] = target
        candidate = esum(dag, platform, trial_frequencies)
        ratio = benefit_to_cost(current, candidate)
        serial += 1
        if candidate.makespan < current.makespan - 1e-9 and abs(candidate.total_energy - current.total_energy) <= 1e-9:
            heapq.heappush(max_heap, (-ratio, serial, task_id, target))
        elif (abs(candidate.makespan - current.makespan) <= 1e-9 and candidate.total_energy < current.total_energy - 1e-9) or candidate.makespan < current.makespan - 1e-9:
            heapq.heappush(min_heap, (ratio, serial, task_id, target))

    for task_id in dag.task_ids:
        probe(task_id)
    while current.makespan > deadline + 1e-9:
        selected = None
        while max_heap and selected is None:
            _, _, task_id, target = heapq.heappop(max_heap)
            if abs(target - (frequencies[task_id] + platform.frequency_step)) <= 1e-9:
                selected = task_id, target
        while selected is None and min_heap:
            _, _, task_id, target = heapq.heappop(min_heap)
            if abs(target - (frequencies[task_id] + platform.frequency_step)) <= 1e-9:
                selected = task_id, target
        if selected is None:
            # Refresh the candidate frontier if the incremental probes have
            # exhausted the heaps before another task becomes useful.
            for candidate_task in dag.task_ids:
                probe(candidate_task)
            if not max_heap and not min_heap:
                return None
            continue
        task_id, target = selected
        frequencies[task_id] = target
        current = esum(dag, platform, frequencies)
        probe(task_id)
    return current