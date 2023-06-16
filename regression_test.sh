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

postfit $RUNCARD1 $REPLICAS
postfit $RUNCARD2 $REPLICAS

vp-comparefits $RUNCARD1 $RUNCARD2 --upload
