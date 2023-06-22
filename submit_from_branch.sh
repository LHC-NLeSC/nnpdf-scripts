#!/bin/bash
#
# Runs a job on a particular branch.
# This assumes that:
# 1. A clone of the repo exists in the current directory, called nnpdf_branch
# 2. An environment exists, built using that clone, called nnpdf-branch
# 3. The repos are in their respective branches.
#
# ****** THIS SCRIPT WILL NOT SWITCH BRANCHES ITSELF!! ******
#
# It will create a copy of the given runcard.
#
# Arguments:
# 1. branch name
# 2. runcard name (without extension)
# 3. the number of replicas to run


[[ $# -lt 3 ]] && { echo "Usage: $0 branch runcard replicas"; exit 1; }

BRANCH=$1
RUNCARD_ORIGINAL=$2
RUNCARD="${RUNCARD_ORIGINAL}_${BRANCH}"
REPLICAS=$3

cp "${RUNCARD_ORIGINAL}.yml" "${RUNCARD}.yml"

ENV="nnpdf-${BRANCH}"
GITDIR="nnpdf_${BRANCH}"

jobname="${RUNCARD}-$(date +%Y%m%d-%H%M%S)"
sbatch --job-name=$jobname --array=1-$REPLICAS run.slurm $RUNCARD $ENV $GITDIR
