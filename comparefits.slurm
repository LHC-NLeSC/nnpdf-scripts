#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --partition thin
#SBATCH --time 04:00:00

# Do the postfit selection and compare the results
#
# ********** UNTESTED **********
#
# Args
# 1, 2. runcard1, runcard2
# 3, 4. fitname1, fitname2
# 5. number of replicas
# 6. environment name
# 7. author name

RUNCARD1=$1
RUNCARD2=$2
FITNAME1=$3
FITNAME2=$4
REPLICAS=$5
ENV=$6
AUTHOR=$7

echo "RUNCARD1: ${RUNCARD1}"
echo "RUNCARD2: ${RUNCARD2}"
echo "FITNAME1: ${FITNAME1}"
echo "FITNAME2: ${FITNAME2}"
echo "REPLICAS: ${REPLICAS}"
echo "ENV: ${ENV}"
echo "AUTHOR: ${AUTHOR}"



TITLE="Regression test"
KEYWORD="report"
REFERENCE_FIT=$RUNCARD1
CURRENT_FIT=$RUNCARD2
REFERENCE_FIT_LABEL="Reference Fit"
CURRENT_FIT_LABEL="Current Fit"

echo "Activating environment..."
source ~/.bashrc
anaconda
conda activate "$ENV"

echo "Extracting timings from replica folders..."
python get_times.py "${RUNCARD1}" "${REPLICAS}" >> "timings_${RUNCARD1}.txt"
python get_times.py "${RUNCARD2}" "${REPLICAS}" >> "timings_${RUNCARD2}.txt"

echo "Evolving all replicas from runcard ${REFERENCE_FIT}..."
evolven3fit $REFERENCE_FIT $REPLICAS
echo "Evolving all replicas from runcard ${CURRENT_FIT}..."
evolven3fit $CURRENT_FIT $REPLICAS

echo "renaming fits to match conventions"
vp-fitrename "${RUNCARD1}" "${FITNAME1}"
vp-fitrename "${RUNCARD2}" "${FITNAME2}"
REFERNCE_FIT=$FITNAME1
CURRENT_FIT=$FITNAME2

echo "Running postfit for runcard ${REFERENCE_FIT}..."
# Note: the replicas we give here are by default the number that pass the checks we're about to do
# Below we ask for at least one.
postfit 1 $REFERENCE_FIT --at-least-nrep
echo "Running postfit for runcard ${CURRENT_FIT}..."
postfit 1 $CURRENT_FIT --at-least-nrep

# NOTE: if you haven't run vp-setupfit before the fit, do it at this point

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

echo "Comparing fits"
vp-comparefits --title "$TITLE" --author "$AUTHOR" --keywords "$KEYWORD" --current_fit_label "$CURRENT_FIT_LABEL" --reference_fit_label "$REFERENCE_FIT_LABEL" $CURRENT_FIT $REFERENCE_FIT
