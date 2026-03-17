#!/bin/sh
# email on start, end, and abortion
#SBATCH --job-name="[FILL IN ANY JOB NAME: ex: training 1]"
##SBATCH --output=job.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=[ENTER YOUR EMAIL ADDRESS]
#SBATCH --partition=schmidt-gpu
#SBATCH --account=pi-dfreedman
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --time=30:00:00

source activate ENV_NAME # activate env as needed - replace ENV_NAME with your env name

module load cuda

python train_ex.py