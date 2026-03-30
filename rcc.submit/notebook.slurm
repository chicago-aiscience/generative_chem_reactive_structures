#!/bin/bash
#SBATCH --job-name=jupyter-launch
#SBATCH --account=pi-mbiroli
#SBATCH --output=jupyter_logs/output-%J.txt
#SBATCH --error=jupyter_logs/error-%J.txt
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=8GB


conda init
source ~/.bashrc

module load python/miniforge-25.3.0
conda activate /project/ai4s-hackathon/ai-sci-hackathon-2026/hackathon-base
source /home/mbiroli/hackathon/my-hack-venv/bin/activate

cd $SLURM_SUBMIT_DIR

HOST_IP=`/sbin/ip route get 8.8.8.8 | awk '{print $7;exit}'`

#Random port access if default port is not available
#PORT_NUM=$(shuf -i15001-30000 -n1)

#Default port is 15021
PORT_NUM=15021

jupyter lab --no-browser --ip=$HOST_IP --port=$PORT_NUM

