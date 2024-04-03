#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=gpu
#SBATCH --cpus-per-task=18
#SBATCH --time=5:00:00
#SBATCH --gpus-per-node=1

TRIES=$1
TID=$2
MODE=${3:-'default'}
REPLICAS=100

module load 2022 TensorFlow/2.11.0-foss-2022a-CUDA-11.7.0 
source ~/nnpdf-env/bin/activate

# Verify GPU usage:
ngpus=$(python3 -c "import tensorflow as tf; print(len(tf.config.list_physical_devices('GPU')))")
if [ "${ngpus}" -eq 0 ]; then
    echo "GPUs not being used!"
else
    echo "Using GPUs! Num GPUs Available: ${ngpus}"
fi

cp nnpdf/n3fit/runcards/hyperopt_studies/renew_hyperopt.yml .
runcard=renew_hyperopt.yml
python create_trial_runcard.py $TRIES $TID $runcard $MODE
runcard=renew_hyperopt_trial_$TID.yml

if [ $MODE == 'hyper' ]; then
    CMD="n3fit $runcard 1 -r $REPLICAS --hyperopt 1"
else
    CMD="n3fit $runcard 1 -r $REPLICAS"
fi
echo "Running:"
echo $CMD
eval $CMD
