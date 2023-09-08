#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=18
#SBATCH --partition gpu
#SBATCH --gpus-per-node=1
#SBATCH --time 00:40:00
#SBATCH --constraint=scratch-node
#SBATCH --output=logs/slurm-%j.out

# Some info on the job...
pwd; hostname; date

ENVNAME=nnpdf-master-gpu
source ~/.bashrc
anaconda
conda activate $ENVNAME

CUDNN_PATH=$(dirname $(python -c "import nvidia.cudnn;print(nvidia.cudnn.__file__)"))
echo $CUDNN_PATH
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib/:$CUDNN_PATH/lib:$LD_LIBRARY_PATH
echo $LD_LIBRARY_PATH

# Verify GPU usage:
python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

RUNCARD=$1
REPLICAS=$2
echo "RUNCARD: $RUNCARD"
echo "REPLICAS: $REPLICAS"
echo "n3fit 'runcards/${RUNCARD}.yml' 1 -r ${REPLICAS}"
#LD_PRELOAD=libmemusage.so n3fit runcards/$RUNCARD.yml 1 -r $REPLICAS
n3fit runcards/$RUNCARD.yml 1 -r $REPLICAS
