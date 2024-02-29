#!/bin/bash
#SBATCH --nodes=1
#SBATCH --partition gpu
#SBATCH --gpus-per-node=4
#SBATCH --time 24:00:00
#SBATCH --output=logs/parallel_slurm-%j.out


# Print job info
echo "Job started on $(hostname) at $(date)"


# conda env
ENVNAME=py_nnpdf-master-gpu

# calc details
RUNCARD="hyper-slowcard.yml"
REPLICAS=100
TRIALS=10
DIR_OUTPUT_NAME="test_hyperopt"
RESTART=false

# number of mongo workers to lauch
N_MONGOWORKERS=4


# activate conda environment
source ~/.bashrc
anaconda
conda activate $ENVNAME


# set up cudnn to run on the gpu
CUDNN_PATH=$(dirname $(python -c "import nvidia.cudnn;print(nvidia.cudnn.__file__)"))
echo "CUDNN path: $CUDNN_PATH"
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib/:$CUDNN_PATH/lib:$LD_LIBRARY_PATH"
echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"

# Verify GPU usage
ngpus=$(python3 -c "import tensorflow as tf; print(len(tf.config.list_physical_devices('GPU')))")
ngpus_list=$(python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))")

echo "List of physical devices '$ngpus_list'"

if [ ${ngpus} -eq 0 ]; then
    echo "GPUs not being used!"
else
    echo "Using GPUs!"
    echo "Num GPUs Available: ${ngpus}"
fi


# Run n3fit

echo "Changing directory to $TMPDIR"
cp "runcards/$RUNCARD" $TMPDIR
if [ ${RESTART} == "true" ]; then
    cp -r $DIR_OUTPUT_NAME $TMPDIR
fi
cd $TMPDIR


echo "Running n3fit..."

if [ ${RESTART} == "true" ]; then

    echo "Restarting job...."
    echo "n3fit '$TMPDIR/$RUNCARD' 1 -r $REPLICAS --hyperopt $TRIALS -o $DIR_OUTPUT_NAME --parallel-hyperopt --num-mongo-workers $N_MONGOWORKERS --restart"

    n3fit "$TMPDIR/$RUNCARD" 1 -r $REPLICAS --hyperopt $TRIALS -o $DIR_OUTPUT_NAME --parallel-hyperopt --num-mongo-workers $N_MONGOWORKERS --restart

else

    echo "n3fit '$TMPDIR/$RUNCARD' 1 -r $REPLICAS --hyperopt $TRIALS -o $DIR_OUTPUT_NAME --parallel-hyperopt --num-mongo-workers $N_MONGOWORKERS"

    n3fit "$TMPDIR/$RUNCARD" 1 -r $REPLICAS --hyperopt $TRIALS -o $DIR_OUTPUT_NAME --parallel-hyperopt --num-mongo-workers $N_MONGOWORKERS

fi


echo "Copying outputs to $SLURM_SUBMIT_DIR ..."
cp -r "$TMPDIR/$DIR_OUTPUT_NAME" $SLURM_SUBMIT_DIR


echo "Returning to $SLURM_SUBMIT_DIR ..."
cd $SLURM_SUBMIT_DIR


echo "Job completed at $(date)"
