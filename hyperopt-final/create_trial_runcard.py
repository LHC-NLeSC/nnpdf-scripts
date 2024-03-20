import json
import yaml
import sys

def update_runcard_from_trial(trial_id, input_runcard_path, hyperopt_file_path, mode):
    hyperopt = mode == "hyper"
    output_runcard_path = input_runcard_path.replace(".yml", f"_trial_{trial_id}.yml")
    # Load hyperopt trials from JSON file
    with open(hyperopt_file_path, 'r') as file:
        trials = json.load(file)

    # Find trial with the given ID
    trial_data = None
    for trial in trials:
        if trial['misc']['tid'] == trial_id:
            trial_data = trial['misc']['space_vals']
            break

    if trial_data is None:
        print(f"No trial found with ID {trial_id}.")
        return

    # Load the input runcard
    with open(input_runcard_path, 'r') as file:
        runcard_data = yaml.safe_load(file)

    # Update runcard parameters with values from the selected trial
    parameters = runcard_data.get('parameters', {})
    for key, value in trial_data.items():
        if key in parameters:
            print(f"Overwriting key {key} with value {value} (original value: {parameters[key]})")
            parameters[key] = value
        # Special handling for nested dictionaries (e.g., optimizer, positivity)
        elif any(key in subdict for subdict in parameters.values() if isinstance(subdict, dict)):
            for subkey, subdict in parameters.items():
                if isinstance(subdict, dict) and key in subdict:
                    parameters[subkey][key] = value

    # correct the activations to be a list
    activation = parameters['activation_per_layer']
    n_layers = len(parameters['nodes_per_layer'])
    parameters['activation_per_layer'] = [activation] * (n_layers - 1) + ['linear']

    # Reduce the search space to just the epochs
    if hyperopt:
        epochs = trial_data['epochs']
        runcard_data['hyperscan_config'] = {
            'stopping': {
                'min_epochs': epochs,
                'max_epochs': epochs + 1,
            }
        }

    # Write the updated runcard to a new YAML file
    with open(output_runcard_path, 'w') as file:
        yaml.safe_dump(runcard_data, file, sort_keys=False)

    print(f"Runcard updated successfully. Output file: {output_runcard_path}")

if __name__ == "__main__":
    print("sys.argv", sys.argv)
    if len(sys.argv) != 5:
        print("Usage: python create_trial_runcard.py <hyperopt_file_path> <trial_id> <input_runcard_path ><mode>")
        sys.exit(1)

    hyperopt_file_path = sys.argv[1]
    trial_id = int(sys.argv[2])
    input_runcard_path = sys.argv[3]
    mode = str(sys.argv[4])

    update_runcard_from_trial(trial_id, input_runcard_path, hyperopt_file_path, mode)
