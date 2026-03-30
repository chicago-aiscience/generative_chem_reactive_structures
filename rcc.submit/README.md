# Submitting Jobs on RCC (Midway)

RCC gives you access to GPUs, which is useful for running multiple training or inference jobs in parallel.

## 1. Log in to RCC

Follow RCC access documentation: https://docs.rcc.uchicago.edu

- Midway3: `ssh -Y [cnetid]@midway3.rcc.uchicago.edu`
- Midway2: `ssh -Y [cnetid]@midway2.rcc.uchicago.edu`

## 2. Transfer files between RCC and local machine

Use `scp` to copy files:

`scp -r [cnetid]@midway3.rcc.uchicago.edu:[rcc_path - source] [local_path - destination]`

## 3. Use Open OnDemand (recommended)

Open OnDemand portal: https://midway3-ondemand.rcc.uchicago.edu

Recommended tools:
- JupyterLab on OnDemand for analysis/training
- Midway Desktop (Linux GUI) for visualization

Setup details: https://docs.rcc.uchicago.edu/open_ondemand/open_ondemand/

If needed, ask mentors or project organizers for help with setup.

## 4. Submit and monitor batch jobs

To run multiple calculations (training/inference) on RCC:

1. SSH to Midway3 (or Midway2).
2. `cd` to your project directory.
3. Make sure `sub.sbatch` exists (an example is included here). This is your Slurm submission script.
4. Ensure `sub.sbatch` contains the command that runs your Python script.
5. Submit the job: `sbatch sub.sbatch`
6. Track job status: `squeue -u [cnetid]`

More on `squeue` status/reason codes: https://docs.rcc.uchicago.edu/slurm/sbatch/?h=squeu#squeue-status-and-reason-codes

General RCC job notes: https://docs.rcc.uchicago.edu/101/jobs/


## 5. Launch a jupter lab session on an RCC compute node

### Via sbatch (recommended)

We have pre-written an sbatch file `notebook.slurm` which does the necessary steps to launch a jupyter lab session on the cluster. Please edit the variables: `account` (and `source [path to venv]` if necessary) in `notebook.slurm`. Then when you run `./launch_notebook.sh` the job request will be automatically submitted and it will return the jupyter lab URLs and the SSH tunnel command. If you are currently accessing the web via the university you should be able to just copy-paste the 10.xx.xxx.xx url in your browser. Otherwise you first need to run the SSH tunnel command on your laptop and then you'll be able to connect via your browser.

### Via the terminal 

Follow the tutorial at: https://docs.rcc.uchicago.edu/software/apps-and-envs/python/#running-jupyter-notebooks.