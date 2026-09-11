"""Shared experiment helpers."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from random import Random
from src.esum import esum
from src.ers import ers
from src.metrics import normalized_energy_rate
from src.models import Platform

def platform(processors, seed, ecr=0.5):
    random = Random(seed)
    return Platform(processors, ps=.03, pind=random.uniform(.03,.07), exponent=random.uniform(2.5,3), capacitance=random.uniform(.08,1.2), ecr=ecr)

def evaluate(dag, processors, extension, seed):
    machine = platform(processors, seed); maximum = esum(dag, machine, {task: machine.fmax for task in dag.tasks}); result = ers(dag, machine, extension * maximum.makespan)
    return maximum, result, 0 if result is None else normalized_energy_rate(maximum, result)