# Submitting Jobs on RCC (Midway)

RCC gives you access to GPUs, which is useful for running multiple training or inference jobs in parallel.

## 1. Log in to RCC

Follow RCC access documentation: https://docs.rcc.uchicago.edu

- Midway3: `ssh -Y [cnetid]@midway3.rcc.uchicago.edu`
- Midway2: `ssh -Y [cnetid]@midway2.rcc.uchicago.edu`

## 2. Transfer files between RCC and local machine

Use `scp` to copy files:

`scp -r [cnetid]@midway3.rcc.uchicago.edu:[rcc_path - source] [local_path - destination]`

## 3. Interactive sessions 

Please do not use the login node to run heavy calculations like model training. You would have to either enter an interactive node (explained here) or submit a batch job (next section) to perform any heavy computation. We have Schmidt GPUs reserved for all participants till April 28th

Use the following command to log into an interactive session. 

`sinteractive --account=ai4s-hackathon --partition=ai4s-hackathon --reservation=ai4s-hackathon`

## 4. Submit and monitor batch jobs

To run multiple calculations (training/inference) on RCC and as an alternative to interactive sessions:

1. SSH to Midway3 (or Midway2).
2. `cd` to your project directory.
3. Make sure `sub.sbatch` exists (an example is included here). This is your Slurm submission script.
4. Ensure `sub.sbatch` contains the command that runs your Python script.
5. Submit the job: `sbatch sub.sbatch`
6. Track job status: `squeue -u [cnetid]`

Use the following account, reservation, and partition to run these jobs (already entered in the `sub.sbatch` script)
```
#SBATCH --account=ai4s-hackathon  
#SBATCH --reservation=ai4s-hackathon  
#SBATCH --partition=ai4s-hackathon
```

More on `squeue` status/reason codes: https://docs.rcc.uchicago.edu/slurm/sbatch/?h=squeu#squeue-status-and-reason-codes

General RCC job notes: https://docs.rcc.uchicago.edu/101/jobs/


## 5. Launch a jupter lab session on an RCC compute node

### Via sbatch (recommended)

We have pre-written an sbatch file `notebook.slurm` which does the necessary steps to launch a jupyter lab session on the cluster. Please edit the variables: `account` (and `source [path to venv]` if necessary) in `notebook.slurm`. Then when you run `./launch_notebook.sh` the job request will be automatically submitted and it will return the jupyter lab URLs and the SSH tunnel command. If you are currently accessing the web via the university you should be able to just copy-paste the 10.xx.xxx.xx url in your browser. If you are running this via Visual Studio Code then VS Code might automatically forward the port and you should be able to just copy-paste the 127.x.x.x address in your browser. Otherwise you first need to run the SSH tunnel command on your laptop and then you'll be able to connect via your browser using the 127.x.x.x address. If the default jupyter port is not available on your machine you can run `LOCAL_TUNNEL_PORT=[whichever local port you want] ./launch_notebook.sh` to use another port.

### Via the terminal 

Follow the tutorial at: https://docs.rcc.uchicago.edu/software/apps-and-envs/python/#running-jupyter-notebooks.

### Remember to close your jupyter session

When you are done, remember to terminate your jupter session so as to not waste any unecessary compute. To do so list your current jobs with `squeue --me` and then cancel the appropriate one with `scancel [JOB_ID]`. 
