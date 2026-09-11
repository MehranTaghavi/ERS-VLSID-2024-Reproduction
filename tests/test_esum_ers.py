import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from motivation.run_motivation_example import motivation_graph
from src.energy import dynamic_task_energy, energy_breakdown
from src.esum import compute_ranks, esum
from src.ers import ers
from src.models import DAG, Edge, Platform, Task


def test_motivation_ranks():
    graph = motivation_graph(); platform = Platform(3, ps=.03, pind=.08, exponent=2.7, capacitance=1.2)
    assert compute_ranks(graph, platform) == {"task_1": 102, "task_4": 77, "task_2": 70, "task_3": 68, "task_5": 66, "task_6": 54, "task_9": 41, "task_7": 34, "task_8": 26, "task_10": 10}


def test_esum_precedence_and_processor_exclusivity():
    graph = motivation_graph(); platform = Platform(3); schedule = esum(graph, platform, {task: 1.0 for task in graph.tasks})
    for edge in graph.edges:
        source, target = schedule.placements[edge.source], schedule.placements[edge.target]
        communication = 0 if source.processor == target.processor else edge.data
        assert target.start >= source.finish + communication - 1e-9
    for processor in range(platform.processor_count):
        intervals = sorted((p.start, p.finish) for p in schedule.placements.values() if p.processor == processor)
        assert all(left[1] <= right[0] + 1e-9 for left, right in zip(intervals, intervals[1:]))


def test_energy_equations():
    graph = DAG({"a": Task("a", 10), "b": Task("b", 20)}, (Edge("a", "b", 4),)); platform = Platform(2, ps=.5, pind=1, exponent=2, capacitance=2, ecr=3)
    schedule = esum(graph, platform, {"a": 1.0, "b": 1.0})
    assert dynamic_task_energy(10, 1.0, platform) == 30
    assert schedule.dynamic_energy >= 30
    assert schedule.static_energy == 2 * .5 * schedule.makespan


def test_safe_ers_meets_deadline():
    graph = motivation_graph(); platform = Platform(3, ps=.03, pind=.08, exponent=2.7, capacitance=1.2); result = ers(graph, platform, 100.0)
    assert result is not None and result.makespan <= 100.0 + 1e-9


# def test_motivation_ers_processor_assignment():
#     graph = motivation_graph(); platform = Platform(3, ps=.03, pind=.08, exponent=2.7, capacitance=1.2, ecr=.5); result = ers(graph, platform, 100.0)
#     assert result is not None
#     assert result.mapping == {
#         "task_1": 0, "task_4": 0, "task_5": 0, "task_9": 0, "task_10": 0,
#         "task_2": 1, "task_6": 1, "task_8": 1,
#         "task_3": 2, "task_7": 2,
#     }