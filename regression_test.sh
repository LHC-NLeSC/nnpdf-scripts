#!/bin/bash
#
# Do the postfit selection and upload the results
#
# ********** UNTESTED **********
#
# Args
# 1. runcard
# 2, 3. branches
# 4. number of replicas


RUNCARD=$1
BRANCH1=$2
BRANCH2=$3
REPLICAS=$4

RUNCARD1="${RUNCARD}_${BRANCH1}" 
RUNCARD2="${RUNCARD}_${BRANCH2}" 

echo "Extracting timings from replica folders..."
echo $RUNCARD1
echo $RUNCARD2
echo $REPLICAS
python get_times.py $RUNCARD1 $REPLICAS >> timings.txt
python get_times.py $RUNCARD2 $REPLICAS >> timings.txt

echo "Evolving all replicas from runcard ${RUNCARD1}..."
evolven3fit $RUNCARD1 $REPLICAS
echo "Evolving all replicas from runcard ${RUNCARD2}..."
evolven3fit $RUNCARD2 $REPLICAS

echo "Running postfit for runcard ${RUNCARD1}..."
# Note: the replicas we give here are by default the number that pass the checks we're about to do
# Below we ask for at least one.
postfit 1 $RUNCARD1 --at-least-nrep
echo "Running postfit for runcard ${RUNCARD2}..."
postfit 1 $RUNCARD2 --at-least-nrep

# setupfit, it's ok to run this after
vp-setupfit "${RUNCARD1}.yml"
vp-setupfit "${RUNCARD2}.yml"

# upload the 2 fits (if it doesn't work because it's not indexed, do cp to conda environment and vp-get instead)
echo "Trying to upload fit..."
vp-upload $RUNCARD1
echo "... uploaded ${RUNCARD1}..."
vp-upload $RUNCARD2
echo "... uploaded ${RUNCARD2}..."

echo "Comparing fits and uploading..."
vp-comparefits $RUNCARD1 $RUNCARD2 --upload
