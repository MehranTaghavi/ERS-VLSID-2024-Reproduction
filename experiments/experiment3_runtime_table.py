"""Experiment 3 runtime entry point."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import platform
from src.dag_generators import gaussian_elimination
from src.esum import esum
from src.ers import ers
from src.gantt import plot_curve
from src.io_utils import save_rows
from src.metrics import measure_runtime

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--trials',type=int,default=250); parser.add_argument('--extension',type=float,default=1.2); parser.add_argument('--ccr',type=float,default=.5); args=parser.parse_args(); sizes=[27,54,77,104,119,152,170,189]; nus=[7,10,12,14,15,17,18,19]; rows=[]
    for size,nu in zip(sizes,nus):
        esum_times=[]; ers_times=[]
        for seed in range(args.trials):
            dag=gaussian_elimination(nu,seed,args.ccr); machine=platform(8,seed); maximum, elapsed=measure_runtime(lambda:esum(dag,machine,{task:machine.fmax for task in dag.tasks})); esum_times.append(elapsed); _,elapsed=measure_runtime(lambda:ers(dag,machine,args.extension*maximum.makespan)); ers_times.append(elapsed)
        rows.append({'|V|':size,'ESUM_runtime_ms':sum(esum_times)/len(esum_times),'ERS_runtime_ms':sum(ers_times)/len(ers_times)})
    output=Path(__file__).parent/'output/experiment3_runtime_table'; save_rows(rows,output/'runtime_ESUM_vs_ERS.csv'); plot_curve(sizes,[row['ERS_runtime_ms'] for row in rows],output/'runtime_vs_tasks.png','Tasks (|V|)','Runtime (ms)','ESUM/ERS runtime')
if __name__=='__main__': main()