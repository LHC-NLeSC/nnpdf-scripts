# nnpdf-scripts

### Setting up the environment
To set up nnpdf on Snellius (only for CPU so far):
1. add contents of .bashrc to your bashrc
2. Clone nnpdf repository: `git clone git@github.com:NNPDF/nnpdf.git`
3. Run `setup.sh nnpdf-dev ./nnpdf` 
    (first argument is the conda environment name, second the directory of the repository)

### Setting up 2 copies for regression testing
One workflow to do the regression tests necessary before a PR can be merged is as follows.
1. Make 2 local copies of the repo, e.g.
```bash
git clone nnpdf nnpdf_master
git clone nnpdf nnpdf_mybranch
```
2. Checkout the appropriate branches in each copy.
3. Create separate conda environments for each copy
```bash
./create_env_from_repo.sh nnpdf_master
./create_env_from_repo.sh nnpdf_mybranch
```

If the environment or runcard is new, make sure to first run one replica separately.
Otherwise when running multiple in parallel, they will all see that some files are missing
and try to download it, and you may get errors.

This setup only has to be done once (if you want to compare different branches,
just check them out, no need to remake the directories or environments).
If you make any changes, do it in the main clone `nnpdf` and pull them in the relevant copy.

Now to run a job specified on a particular `runcard`, using both branches,
```bash
./submit_from_branch.sh master runcard 100
./submit_from_branch.sh mybranch runcard 100
```

### Running a regression test
Once set up, to run a regression test:

```bash
./regression_test.sh runcard master mybranch Nreplicas 1
```
will submit two jobs, one with each branch.

Once done,
```bash
./regression_test.sh runcard master mybranch Nreplicas 2
```
will submit a job to further process the fits and do a comparison.

Finally,
```bash
./regression_test.sh runcard master mybranch Nreplicas 3
```
will upload the report (directly, not in a job).

The output of the last step includes a link to the report, and in the second step a 
`timings.txt` is created that has the timings.
