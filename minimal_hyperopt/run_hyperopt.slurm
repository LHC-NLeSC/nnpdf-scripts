#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=18
#SBATCH --partition gpu
#SBATCH --gpus-per-node=1
#SBATCH --time 01:00:00
#SBATCH --output=logs/slurm-%j.out

# Some info on the job...
pwd; hostname; date

# check arguments
if [ "$#" -ne 3 ]; then
    echo "Illegal number of parameters"
    echo "Usage: run_hyperopt.sh <runcard> <replicas> <trials>"
    exit 1
fi

RUNCARD=$1
REPLICAS=$2
TRIALS=$3
echo "RUNCARD: $RUNCARD"
echo "REPLICAS: $REPLICAS"
echo "TRIALS: $TRIALS"

# activate conda environment
ENVNAME=nnpdf-master-gpu
source ~/.bashrc
anaconda
conda activate $ENVNAME

# set up cudnn to run on the gpu
CUDNN_PATH=$(dirname $(python -c "import nvidia.cudnn;print(nvidia.cudnn.__file__)"))
echo $CUDNN_PATH
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib/:$CUDNN_PATH/lib:$LD_LIBRARY_PATH
echo $LD_LIBRARY_PATH

echo "n3fit 'runcards/${RUNCARD}.yml' 1 -r ${REPLICAS} --hyperopt ${TRIALS}"
n3fit runcards/$RUNCARD.yml 1 -r $REPLICAS --hyperopt $TRIALS
