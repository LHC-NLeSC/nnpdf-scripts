#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
##SBATCH --cpus-per-task=16
#SBATCH --partition thin
#SBATCH --time 120:00:00
#SBATCH --output=logs/slurm-%j.out


# Constants, change these manually!
ENVNAME=nnpdf-master-gpu
#GITDIR=/home/aronjan/experiments/nnpdf_master
GITDIR=/home/crocha/nnpdfgit/experiments/nnpdf_master

# print job info
pwd; hostname; date

# print git info
echo "\n\nLast commit: "
git -C ${GITDIR} log -1
echo "\n\nStatus: "
git -C ${GITDIR} status -uno

# also print git info of the runcard, assuming this is run from the scripts repo
echo "\n\nRuncard git info: "
git log -1
git status -uno

# check if at least 3 arguments were passed
if [ "$#" -lt 4 ]; then
    echo "Illegal number of parameters"
    echo "Usage: cpu_run_hyperoptrun_hyperopt_with_restarts.sh <runcard> <replicas> <trials> [-n <name>] <restart>"
    exit 1
fi

RUNCARD=$1
REPLICAS=$2
TRIALS=$3
if [ "$#" -eq 5 ]; then
    NAME=$5
fi
if [ "$#" -eq 6 ]; then
    echo "Restarting job...."
    NAME=$5
    RESTART=$6
fi

echo "RUNCARD: $RUNCARD"
echo "REPLICAS: $REPLICAS"
echo "TRIALS: $TRIALS"

# activate conda environment
source ~/.bashrc
anaconda
conda activate $ENVNAME

# Copy the runcard under the specified name, if given, to avoid different jobs writing to the same directory
if [ "$#" -eq 5 ]; then
    mkdir -p runcards/temp
    cp runcards/$RUNCARD.yml runcards/temp/$NAME.yml
    RUNCARD=temp/$NAME
    RENAMED=1
else
    RENAMED=0
fi

# set up cudnn to run on the gpu
CUDNN_PATH=$(dirname $(python -c "import nvidia.cudnn;print(nvidia.cudnn.__file__)"))
echo $CUDNN_PATH
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib/:$CUDNN_PATH/lib:$LD_LIBRARY_PATH
echo $LD_LIBRARY_PATH

# Verify GPU usage:
ngpus=$(python3 -c "import tensorflow as tf; print(len(tf.config.list_physical_devices('GPU')))")

if [ "${ngpus}" -eq 0 ]; then
    echo "GPUs not being used!"
else
    echo "Using GPUs!"
    echo "Num GPUs Available: ${ngpus}"
fi

if [ -n "${RESTART}" ]; then
    echo "Restarting job...."
    echo "n3fit 'runcards/${RUNCARD}.yml' 1 -r ${REPLICAS} --hyperopt ${TRIALS} -o ${NAME} --restart"
    n3fit runcards/$RUNCARD.yml 1 -r $REPLICAS --hyperopt $TRIALS -o ${NAME} --restart
else
    echo "n3fit 'runcards/${RUNCARD}.yml' 1 -r ${REPLICAS} --hyperopt ${TRIALS}"
    n3fit runcards/$RUNCARD.yml 1 -r $REPLICAS --hyperopt $TRIALS
fi

# move the runcard directory to the results directory
mkdir -p results
if [ "$RENAMED" -eq 1 ]; then
    mv $NAME results/$NAME
else
    mv $RUNCARD results/$RUNCARD
fi

# delete the copied runcard
if [ "$RENAMED" -eq 1 ]; then
    rm runcards/temp/$NAME.yml
fi
