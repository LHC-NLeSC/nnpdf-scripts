for runcard in Basic_runcard Basic_runcard_frac1 Basic_runcard_nopositivity Basic_runcard_patience
do
    echo "Comparing $runcard"
    for replica in 1 2 3
    do
        old=master/$runcard/nnfit/replica_$replica
        new=refactor/$runcard/nnfit/replica_$replica
        for file in $old/*
        do
            filename=$(basename $file)
            oldfile=$old/$filename
            newfile=$new/$filename
            diff $oldfile $newfile | grep -v validphys | grep -v nnpdf | grep -v replica_set_to_replica_fitted | grep -v replica_set | grep -v replica_fitted | grep -v Total
        done
    done
done
