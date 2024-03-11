#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=gpu
#SBATCH --cpus-per-task=72
#SBATCH --time=120:00:00
#SBATCH --gpus-per-node=4

REPLICAS=100
WORKERS=4
TRIALS=2000

# Load conda
source ~/.bashrc
anaconda
conda activate nnpdf-311

# Verify GPU usage:
ngpus=$(python3 -c "import tensorflow as tf; print(len(tf.config.list_physical_devices('GPU')))")
if [ "${ngpus}" -eq 0 ]; then
    echo "GPUs not being used!"
else
    echo "Using GPUs! Num GPUs Available: ${ngpus}"
fi

cp nnpdf/n3fit/runcards/hyperopt_studies/renew_hyperopt.yml .
runcard=renew_hyperopt.yml

CMD="n3fit $runcard 1 -r $REPLICAS --hyperopt $TRIALS --parallel-hyperopt --num-mongo-workers $WORKERS"
echo "Running:"
echo $CMD
eval $CMD
