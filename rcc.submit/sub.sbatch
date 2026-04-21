#!/bin/sh
# email on start, end, and abortion
#SBATCH --job-name="[FILL IN ANY JOB NAME: ex: training 1]"
#SBATCH --mail-type=ALL
#SBATCH --mail-user=[ENTER YOUR EMAIL ADDRESS]
#SBATCH --account=ai4s-hackathon
#SBATCH --reservation=ai4s-hackathon  
#SBATCH --partition=ai4s-hackathon
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --time=30:00

# If you want the output to be in a certain file, remove one of the # in the next line
##SBATCH --output=[output filename]

source activate [ENV_NAME] # activate env as needed - replace ENV_NAME with your env name

module load cuda

python train_ex.py
