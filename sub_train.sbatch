#!/bin/sh
# email on start, end, and abortion
#SBATCH --job-name=[NAME OF JOB]
#SBATCH --mail-type=ALL
#SBATCH --mail-user=[YOUR EMAIL]
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

# source activate [ENV_NAME] # activate env as needed - replace ENV_NAME with your env name
# module load python/miniforge-25.3.0
# conda init
# source ~/.bashrc
conda activate /project/ai4s-hackathon/ai-sci-hackathon-2026/hackathon-base-miniforge

module load cuda

python Code/Examples/train_and_eval_egnn.py   --pkl Data/transition1x/train.pkl   --atom-count 10   --epochs 3   --train-samples 200   --eval-samples 100   --out-dir outputs_xyz/