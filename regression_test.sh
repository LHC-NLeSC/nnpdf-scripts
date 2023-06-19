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

RUNCARD1="${RUNCARD}_%{BRANCH1}" 
RUNCARD2="${RUNCARD}_%{BRANCH2}" 

echo "Evolving all replicas from runcard ${RUNCARD1}..."
evolven3fit $RUNCARD1 $REPLICAS
echo "Evolving all replicas from runcard ${RUNCARD2}..."
evolven3fit $RUNCARD2 $REPLICAS

echo "Running postfit for runcard ${RUNCARD1}..."
postfit $RUNCARD1 $REPLICAS
echo "Running postfit for runcard ${RUNCARD2}..."
postfit $RUNCARD2 $REPLICAS

echo "Comparing fits and uploading..."
vp-comparefits $RUNCARD1 $RUNCARD2 --upload
