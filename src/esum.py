"""ESUM: rank-based earliest-finish list scheduling."""
from typing import Callable, Iterable, Mapping, Tuple
from .energy import energy_breakdown, execution_time
from .models import DAG, Platform, Placement, Schedule

def compute_ranks(dag: DAG, platform: Platform) -> dict[str, float]:
    # استخراج پراپرتی‌ها فقط یک بار برای جلوگیری از محاسبه مجدد در حلقه
    data = dag.edge_data
    successors = dag.successors
    task_ids = dag.task_ids
    
    ranks: dict[str, float] = {}

    # محاسبه میانگین نرخ انتقال
    rates = []
    if platform.processor_count > 1:
        for i in range(platform.processor_count):
            for j in range(platform.processor_count):
                if i != j:
                    rates.append(platform.transfer_rate(i, j))
        avg_transfer_rate = sum(rates) / len(rates)
    else:
        avg_transfer_rate = 1.0

    def rank(task_id: str) -> float:
        if task_id in ranks:
            return ranks[task_id]
        
        # استفاده از دیکشنری محلی successors
        ranks[task_id] = dag.tasks[task_id].wcet + max(
            (data[(task_id, child)] / avg_transfer_rate + rank(child) for child in successors[task_id]),
            default=0.0,
        )
        return ranks[task_id]

    for task_id in task_ids:
        rank(task_id)
    return ranks

def communication_time_for_edge(platform: Platform, source: int, target: int, data: float) -> float:
    return 0.0 if source == target else data / platform.transfer_rate(source, target)

# def esum(dag: DAG, platform: Platform, frequencies: Mapping[str, float]) -> Schedule:
#     """Run Algorithm 1 for the supplied per-task frequency table."""
#     if set(frequencies) != set(dag.tasks):
#         raise ValueError("A frequency is required for every task")
    
#     ranks = compute_ranks(dag, platform)
    
#     # --- بهینه‌سازی حیاتی O(1) ---
#     # فراخوانی پراپرتی‌های گراف خارج از حلقه برای جلوگیری از اجرای میلیاردها دستور اضافی
#     task_ids = dag.task_ids
#     data = dag.edge_data
#     predecessors = dag.predecessors
#     dag_entry = dag.entry
#     dag_exit = dag.exit
#     # ----------------------------------------
    
#     order = sorted(task_ids, key=lambda task: (-ranks[task], task_ids.index(task)))
#     available = [0.0] * platform.processor_count
#     placements: dict[str, Placement] = {}
    
#     for task_id in order:
#         candidates = []
#         duration = execution_time(dag.tasks[task_id].wcet, frequencies[task_id], platform)
#         task_preds = predecessors[task_id]  # استخراج پیش‌نیازهای تسک فعلی در متغیر محلی
        
#         for processor in range(platform.processor_count):
#             predecessor_ready = max(
#                 (placements[parent].finish + communication_time_for_edge(
#                     platform, placements[parent].processor, processor, data[(parent, task_id)]
#                 ) for parent in task_preds),
#                 default=0.0,
#             )
#             # استفاده از متغیر محلی dag_entry
#             start = max(available[processor], predecessor_ready) if task_id != dag_entry else 0.0
            
#             hosts_predecessor = any(placements[parent].processor == processor for parent in task_preds)
#             candidates.append((start + duration, 0 if hosts_predecessor else 1, processor, start))
        
#         finish, _, processor, start = min(candidates)
#         placements[task_id] = Placement(task_id, processor, frequencies[task_id], start, finish)
#         available[processor] = finish
        
#     makespan = placements[dag_exit].finish
#     partial = Schedule(placements, ranks, makespan, 0.0, 0.0, 0.0, dict(frequencies))
#     static, dynamic, total = energy_breakdown(dag, platform, partial)
    
#     return Schedule(placements, ranks, makespan, static, dynamic, total, dict(frequencies))

TieBreakingStrategy = Callable[[Iterable[Tuple[float, bool, int, float]]], Tuple[float, bool, int, float]]

def default_tie_breaker(candidates: Iterable[Tuple[float, bool, int, float]]) -> Tuple[float, bool, int, float]:
    """
    Default tie-breaking strategy for ESUM.
    Criteria in order of priority:
    1. Minimum Effective Finish Time (EFT) (index 0).
    2. Locality: Prefer processor hosting a predecessor (False/True mapped to 1/0 penalty).
    3. Deterministic order: Lowest processor ID (index 2).
    """
    return min(candidates, key=lambda c: (c[0], 0 if c[1] else 1, c[2]))

def esum(dag: DAG, platform: Platform, frequencies: Mapping[str, float], tie_breaker: TieBreakingStrategy = default_tie_breaker) -> Schedule:
    """Run Algorithm 1 for the supplied per-task frequency table."""
    if set(frequencies) != set(dag.tasks):
        raise ValueError("A frequency is required for every task")
        
    ranks = compute_ranks(dag, platform)
    
    # ---   O(1) ---
    task_ids = dag.task_ids
    data = dag.edge_data
    predecessors = dag.predecessors
    dag_entry = dag.entry
    dag_exit = dag.exit
    # ----------------------------------------
    
    order = sorted(task_ids, key=lambda task: (-ranks[task], task_ids.index(task)))
    available = [0.0] * platform.processor_count
    placements: dict[str, Placement] = {}
    
    for task_id in order:
        candidates = []
        duration = execution_time(dag.tasks[task_id].wcet, frequencies[task_id], platform)
        task_preds = predecessors[task_id]
        
        for processor in range(platform.processor_count):
            predecessor_ready = max(
                (placements[parent].finish + communication_time_for_edge(
                    platform, placements[parent].processor, processor, data[(parent, task_id)]
                ) for parent in task_preds),
                default=0.0,
            )
            start = max(available[processor], predecessor_ready) if task_id != dag_entry else 0.0
            
            # ثبت وضعیت locality به عنوان یک بولین (بدون هاردکد کردن پنالتی)
            hosts_predecessor = any(placements[parent].processor == processor for parent in task_preds)
            candidates.append((start + duration, hosts_predecessor, processor, start))
        
        # تفویض انتخاب نهایی به استراتژی تزریق‌شده
        finish, _, processor, start = tie_breaker(candidates)
        placements[task_id] = Placement(task_id, processor, frequencies[task_id], start, finish)
        available[processor] = finish
        
    makespan = placements[dag_exit].finish
    partial = Schedule(placements, ranks, makespan, 0.0, 0.0, 0.0, dict(frequencies))
    static, dynamic, total = energy_breakdown(dag, platform, partial)
    
    return Schedule(placements, ranks, makespan, static, dynamic, total, dict(frequencies))