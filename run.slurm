#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --partition thin
#SBATCH --time 02:00:00
#SBATCH --constraint=scratch-node

RUNCARD=$1
ENV=$2
GITDIR=$3

# Some info on the job...
pwd; hostname; date
echo "Environment $ENV"
echo "Runcard $RUNCARD"
echo "Last commit: "
git -C ${GITDIR} log -1

source ~/.bashrc
anaconda
conda activate "$ENV"

vp-setupfit "${RUNCARD}.yml"

copy_data_to_local_scratch $ENV
n3fit "${RUNCARD}.yml" $SLURM_ARRAY_TASK_ID
