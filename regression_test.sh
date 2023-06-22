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

echo "Running postfit for runcard ${RUNCARD1}..."
# Note: the replicas we give here are by default the number that pass the checks we're about to do
# Below we ask for at least one.
postfit 1 $RUNCARD1 --at-least-nrep
echo "Running postfit for runcard ${RUNCARD2}..."
postfit 1 $RUNCARD2 --at-least-nrep

echo "Evolving all replicas from runcard ${RUNCARD1}..."
evolven3fit $RUNCARD1 $REPLICAS
echo "Evolving all replicas from runcard ${RUNCARD2}..."
evolven3fit $RUNCARD2 $REPLICAS

# if you haven't run vp-setupfit before the fit, do it at this point

# upload the 2 fits, it may fail indexing, keep trying until it works
# see https://github.com/NNPDF/nnpdf/issues/1079
echo "Trying to upload fit..."
while [[ $? -eq 0 ]]
do
    vp-upload ${RUNCARD1}
    sleep 20s ; # don't want to chain uploads...
done
echo "... uploaded ${RUNCARD1}..."
while [[ $? -eq 0 ]]
do
    vp-upload ${RUNCARD2}
    sleep 20s ; # don't want to chain uploads...
done
echo "... uploaded ${RUNCARD2}..."

echo "Comparing fits and uploading..."
vp-comparefits $RUNCARD1 $RUNCARD2 --upload
