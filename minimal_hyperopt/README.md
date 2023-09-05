# Running

To start a minimal hyperopt run with R replicas and T trials, and optionally naming the output, run
```
sbatch run_hyperopt.slurm minimal_hyperopt R T -n name
```

The script should be run from this directory, and attempts to keep it clean by moving the results to
a results subdirectory and storing the logs in a logs directory.

Make sure to adjust the time reserved appropriately.

# Timings

| replicas | sec/100 epochs (fold 1) | hours/trial (extrapolated) | max trials in 72h |
| --- | --- | --- | --- |
10 | 17 | 3.2 | 22 |
20 | 30 | 5.6 | 12 |
40 | 56 | 10.5 | 6 |

# Runcards

- NNPDF_hyperopt.yml
    This is the runcard from n3fit/runcards/reproduce, with minimal adaptations to the new syntax
- minimal_hyperopt.yml
    Here everything has been set to the optimal values, except the architecture.
    Specifically we fix the number of layers to 2, and so vary only the
    number of units in those two layers.
