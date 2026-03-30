# Submitting Jobs on RCC (Midway)

RCC gives you access to GPUs, which is useful for running multiple training or inference jobs in parallel.

## 1. Log in to RCC

Follow RCC access documentation: https://docs.rcc.uchicago.edu

- Midway3: `ssh -Y [cnetid]@midway3.rcc.uchicago.edu`
- Midway2: `ssh -Y [cnetid]@midway2.rcc.uchicago.edu`

## 2. Transfer files between RCC and local machine

Use `scp` to copy files:

`scp -r [cnetid]@midway3.rcc.uchicago.edu:[rcc_path - source] [local_path - destination]`


## 3. Submit and monitor batch jobs

To run multiple calculations (training/inference) on RCC:

1. SSH to Midway3 (or Midway2).
2. `cd` to your project directory.
3. Make sure `sub.sbatch` exists (an example is included here). This is your Slurm submission script.
4. Ensure `sub.sbatch` contains the command that runs your Python script.
5. Submit the job: `sbatch sub.sbatch`
6. Track job status: `squeue -u [cnetid]`

More on `squeue` status/reason codes: https://docs.rcc.uchicago.edu/slurm/sbatch/?h=squeu#squeue-status-and-reason-codes

General RCC job notes: https://docs.rcc.uchicago.edu/101/jobs/


## 4. Launch a jupyter session on RCC

```
module load python/miniforge-25.3.0
source ~/my_hackaton_env/bin/activate

HOST_IP=`/sbin/ip route get 8.8.8.8 | awk '{print $7;exit}'`
echo $HOST_IP
'''

The HOST_IP should be either 128.135.x.y (an external address), or 10.50.x.y (on-campus address). Then launch jupyter with

```
jupyter-lab --no-browser --ip=$HOST_IP --port=15021
'''

which will give you two URLs with a token, one with the external address 128.135.x.y, and another with the on-campus address 10.50.x.y, or with your local host 127.0.0.*. The on-campus address 10.50.x.y is only valid when you are connecting to Midway2 or Midway3 via VPN.

Open a web browser on your local machine with the returned URLs.

If you are using on-campus network or VPN, you can copy-paste (or Ctrl + click) the URL with the external address, or the URL with the on-campus address into the browser's address bar.

Without VPN, you need to use SSH tunneling to connect to the Jupyter server launched on the Midway2 (or Midway3) login or compute nodes in Step 3 from your local machine. To do that, open another terminal window on your local machine and run

```
ssh -N -f -L 15021:<HOST_IP>:15021 <your-CNetID>@midway3.rcc.uchicago.edu
'''
where HOST_IP is the external IP address of the login node obtained from Step 2, and 15021 is the port number used in Step 3.
This command will create an SSH connection from your local machine to Midway login or compute nodes and forward the 15021 port to your local host at port 15021. The port number should be consistent across all the steps (15021 in this example). You can find out the meaning for the arguments used in this command at explainshell.com.

After successfully logging with 2FA as usual, you will be able to open the URL http://127.0.0.1:15021/?token=...., or equivalently, localhost:15021/?token=.... in the browser on your local machine.
```
## 5. Use Open OnDemand (optional way to run jupyter sessions)

Open OnDemand portal: https://midway3-ondemand.rcc.uchicago.edu

Recommended tools:
- JupyterLab on OnDemand for analysis/training
- Midway Desktop (Linux GUI) for visualization

Setup details: https://docs.rcc.uchicago.edu/open_ondemand/open_ondemand/

If needed, ask mentors or project organizers for help with setup.