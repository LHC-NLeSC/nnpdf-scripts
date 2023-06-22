import argparse
import os
import json
import numpy as np

def extract_times(runcard, replicas):
    directory = f"{runcard}/nnfit/"
    walltimes = []
    cputimes = []
    print(f"Timings for runcard {runcard}:")

    for i in range(1, replicas+1):
        replica_dir = os.path.join(directory, f'replica_{i}')
        json_file = f"{replica_dir}/{runcard}.json"

        with open(json_file, 'r') as f:
            data = json.load(f)

        walltimes.append(data['timing']['walltime']['Total'])
        cputimes.append(data['timing']['cputime']['Total'])

    wall_mean = np.mean(np.array(walltimes))
    cpu_mean = np.mean(np.array(cputimes))

    wall_std = np.std(np.array(walltimes))
    cpu_std = np.std(np.array(cputimes))

    print(f"Wall time, mean: {wall_mean}, std: {wall_std}")
    print(f"CPU time, mean: {cpu_mean}, std: {cpu_std}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('runcard')
    parser.add_argument('replicas', type=int)

    args = parser.parse_args()

    extract_times(args.runcard, args.replicas)


if __name__ == '__main__':
    main()
