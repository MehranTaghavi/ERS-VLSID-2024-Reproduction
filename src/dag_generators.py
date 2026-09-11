"""Random and benchmark DAG generators."""
from random import Random
from .models import DAG, Edge, Task

def _randomize(ids, pairs, seed, ccr):
    random = Random(seed)
    tasks = {task: Task(task, float(random.randint(10, 100))) for task in ids}
    average = sum(task.wcet for task in tasks.values()) / len(tasks)
    edges = tuple(Edge(source, target, float(random.randint(10, 100) * ccr * average / 55.0)) for source, target in pairs)
    return DAG(tasks, edges)

def gaussian_elimination(matrix_size: int, seed: int = 0, ccr: float = .5) -> DAG:
    count = (matrix_size * matrix_size + matrix_size - 2) // 2
    edge_count = matrix_size * matrix_size - matrix_size - 1
    ids = [f"task_{index}" for index in range(1, count + 1)]
    pairs = [(ids[index], ids[index + 1]) for index in range(count - 1)]
    pairs.extend((ids[source], ids[target]) for source in range(count) for target in range(source + 2, count))
    return _randomize(ids, pairs[:edge_count], seed, ccr)

def laplace(phi: int, seed: int = 0, ccr: float = .5) -> DAG:
    ids = [f"task_{row * phi + column + 1}" for row in range(phi) for column in range(phi)]
    pairs = []
    for row in range(phi):
        for column in range(phi):
            index = row * phi + column
            if column + 1 < phi: pairs.append((ids[index], ids[index + 1]))
            if row + 1 < phi: pairs.append((ids[index], ids[index + phi]))
    return _randomize(ids, pairs, seed, ccr)

def random_dag(task_count: int, seed: int = 0, ccr: float = .5) -> DAG:
    random = Random(seed); ids = [f"task_{index}" for index in range(1, task_count + 1)]
    pairs = [(ids[index], ids[index + 1]) for index in range(task_count - 1)]
    pairs.extend((ids[source], ids[target]) for source in range(task_count - 2) for target in range(source + 2, task_count) if random.random() < 4 / task_count)
    return _randomize(ids, pairs, seed, ccr)