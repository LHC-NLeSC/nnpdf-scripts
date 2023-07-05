# This script contains all of the steps to perform a regression test
# Steps:
# 1. Submit fitting jobs with both branches
# 2. Run vp-comparefits on the fit results
# 3. Upload the fit

# CHANGE THESE MANUALLY
AUTHOR="Aron Jansen"
INITIALS="aj"


[[ $# -lt 5 ]] && { echo "Usage: $0 runcard branch1 branch2 replicas step"; exit 1; }


RUNCARD_ORIGINAL=$1
BRANCH1=$2
BRANCH2=$3
REPLICAS=$4
STEP=$5

RUNCARD1="${RUNCARD_ORIGINAL}_${BRANCH1}"
RUNCARD2="${RUNCARD_ORIGINAL}_${BRANCH2}"

ENV1="nnpdf-${BRANCH1}"
ENV2="nnpdf-${BRANCH2}"

function runfits {
    run_on_branch $RUNCARD1 $ENV1 $BRANCH1
    run_on_branch $RUNCARD2 $ENV2 $BRANCH2
}

function comparefits {
    today=$(date +'%y%m%d')

    KEYWORDS1="regression-${BRANCH1}"
    KEYWORDS2="regression-${BRANCH2}"

    FITNAME1="${today}-${INITIALS}-${KEYWORDS1}-001"
    FITNAME2="${today}-${INITIALS}-${KEYWORDS2}-001"

    jobname="compare_${BRANCH1}_${BRANCH2}_${today}"
    sbatch --job-name=$jobname comparefits.slurm $RUNCARD1 $RUNCARD2 $FITNAME1 $FITNAME2 $REPLICAS $ENV1 "$AUTHOR"
}

function upload {
    activate_env
    vp-upload output
}

function activate_env {
    source ~/.bashrc
    anaconda
    conda activate "$ENV1"
}

function run_on_branch {
    RUNCARD=$1
    ENV=$2
    BRANCH=$3

    cp "${RUNCARD_ORIGINAL}.yml" "${RUNCARD}.yml"
    jobname="${RUNCARD}-$(date +%Y%m%d-%H%M%S)"
    runcard=$RUNCARD
    env=$ENV
    gitdir="nnpdf_${BRANCH}"
    outdir="logs/${RUNCARD_ORIGINAL}/${BRANCH}"
    mkdir -p "${outdir}"
    sbatch --job-name=$jobname --array=1-$REPLICAS --output="${outdir}/output_%A_%a.out" run.slurm $runcard $env $gitdir
}

case $STEP in
  1) runfits ;;
  2) comparefits ;;
  3) upload ;;
  *) echo "Invalid step number. Please provide a step number (1, 2, or 3)." ;;
esac
