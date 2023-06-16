# nnpdf-scripts

### Setting up the environment
To set up nnpdf on Snellius (only for CPU so far):
1. add contents of .bashrc to your bashrc
2. Clone nnpdf repository: `git clone git@github.com:NNPDF/nnpdf.git`
3. Run `setup.sh nnpdf-dev ./nnpdf` 
    (first argument is the conda environment name, second the directory of the repository)

### Running a regression test
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

This only has to be done once (if you want to compare different branches, just check them out, no need to remake the directories or environments).
If you make any changes, do it in the main clone `nnpdf` and pull them in the relevant copy.

Now to run a job specified on a particular `runcard`, using both branches,
```bash
./submit_from_branch.sh master runcard 100
./submit_from_branch.sh mybranch runcard 100
```

After this it's still necessary to do a postfit.
