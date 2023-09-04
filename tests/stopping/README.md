I took the Basic_runcard.yml, enabled multi replica fits by adding:
```
fitting:
  savepseudodata: false

parallel_models: true
same_trvl_per_replica: true
```

And I wanted the stopping conditions to trigger, so I changed:
```
parameters:
  nodes_per_layer: [8]
  activation_per_layer: ['linear']
  stopping_patience: 0.05
```

That's the base case, and then there are 3 copies with each of these changes in turn:
`Basic_runcard_frac1.yml`:
```
dataset_inputs:
- { dataset: SLACP_dwsh, frac: 1.0}
- { dataset: NMCPD_dw, frac: 1.0 }
```

`Basic_runcard_nopositivity.yml`:
```
positivity:
  posdatasets: []
```

`Basic_runcard_patience.yml`:
```
parameters:
  stopping_patience: 1.0
```


Then to test, when checked out on master I run
```
./test_stopping.sh master
```
to run them all on master, then checkout to the refactored branch and run
```
./test_stopping.sh refactor
```
and finally to compare them,
```
./compare_stopping.sh
```
