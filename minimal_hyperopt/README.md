# Runcards

- NNPDF_hyperopt.yml
    This is the runcard from n3fit/runcards/reproduce, with minimal adaptations to the new syntax
- minimal_hyperopt.yml
    Here everything has been set to the optimal values, except the architecture.
    Specifically we fix the number of layers to 2, and so vary only the
    number of units in those two layers.

The run we want to do is with e.g. 20 replicas and 10 trials (??)
```
sbatch run_hyperopt.slurm minimal_hyperopt 20 10
```
