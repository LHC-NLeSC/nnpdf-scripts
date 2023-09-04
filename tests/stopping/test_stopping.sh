name=$1
mkdir -p $name
# run all 4 runcards
for runcard in Basic_runcard Basic_runcard_frac1 Basic_runcard_nopositivity Basic_runcard_patience
do
    echo "Running $runcard"
    n3fit $runcard.yml 1 -r 3
    # move results to their own folder
    mv $runcard $name
done
