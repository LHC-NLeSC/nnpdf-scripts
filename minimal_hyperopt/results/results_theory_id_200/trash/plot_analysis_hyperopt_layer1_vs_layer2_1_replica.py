import json
from typing import Tuple, List
import pandas as pd


def filter_data(path_to_file: str, n_trials: int) -> Tuple[pd.DataFrame, List]:
    """Function to filter data out from hyperopt run.

        Args:
            path_to_file (str): file to read hyperopt data from
            n_trials (int): Number of hyperopt trials

        Returns:
            A pandas DataFrame containing filtered data
    """

    # open the json file and transform it into a list of dictionaries
    with open(path_to_file, 'r') as f:
        data = json.load(f)

    print(data[25])

    average_over_rep_and_k_hyper_losses = []
    hidden_layers_1 = []
    hidden_layers_2 = []
    trials = []

    for n in range(n_trials):

        # hyper loss averaged over replicas first and then over k-folds
        loss = data[n]['result']['loss']

        # size of hidden layers
        layer_size_1 = data[n]['misc']['space_vals']['nodes_per_layer'][0]
        layer_size_2 = data[n]['misc']['space_vals']['nodes_per_layer'][1]

        # trial number
        trial_id = data[n]['tid']

        average_over_rep_and_k_hyper_losses.append(loss)
        hidden_layers_1.append(layer_size_1)
        hidden_layers_2.append(layer_size_2)
        trials.append(trial_id)

    min_loss = min(average_over_rep_and_k_hyper_losses)
    min_loc = average_over_rep_and_k_hyper_losses.index(min_loss)
    min_layer_size_1 = hidden_layers_1[min_loc]
    min_layer_size_2 = hidden_layers_2[min_loc]
    hyperopt_res = [min_layer_size_1, min_layer_size_2, min_loss]

    print("========================================================================================")
    print(f"Minimum value of the hyper loss (averaged over replicas and k-folds): {min_loss}")
    print(f"Optimum # of nodes per layer: {min_layer_size_1, min_layer_size_2}")
    print(f"Optimum Trial #: {min_loc}")
    print(f"Total # of Trials: {n_trials}")
    print("========================================================================================")
    #print("Optimum # of nodes per layer from previous hyperopt with 1 replica: (25, 20)")
    #print("========================================================================================")

    # creating a simple DataFrame containing all data
    df = pd.DataFrame(
        {'Trial': trials,
         'Hidden layer #1 size': hidden_layers_1,
         'Hidden layer #2 size': hidden_layers_2,
         'Average Hyper Loss': average_over_rep_and_k_hyper_losses}
    )

    # Replace 'inf' strings with NaN
    df = df.replace(float('inf'), pd.NA)

    # Drop rows containing NaN values in any column
    df = df.dropna(how='any')

    # Reset the index if needed
    df.reset_index(drop=True, inplace=True)

    return df, hyperopt_res


import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import scipy.stats as sps
import matplotlib.patches as patches
from matplotlib.lines import Line2D

# path to 'tries.json' file
path_to_file = 'hyperopt_1_rep_1000_trials_13_Sep_2023_parallel_models_false/nnfit/replica_1/tries.json'

# number of Trials
n_trials = 52

df, hyperopt_res = filter_data(path_to_file, n_trials)

print(df, hyperopt_res)

# Simple 3D Histogram plot
#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
#
#ax.bar3d(df['Hidden layer #1 size'], df['Hidden layer #2 size'], np.zeros_like(df['Average Loss']), dx=3, dy=3, dz=df['Average Loss'], shade=True)
#ax.set_xlabel('# of units Layer 1')
#ax.set_ylabel('# of units Layer 2')
#ax.set_zlabel('Final Hyper Loss')
#plt.title('Hyperopt scan with 10 replicas')
#plt.xlim(5, 50)
#plt.ylim(5, 50)
#
#plt.show() # or:
##fig.savefig('3D.png')

# Contour 2D plot

x = df['Hidden layer #1 size']
y = df['Hidden layer #2 size']
z = df['Average Hyper Loss']

offset = .25
xmin = x.min()-offset
xmax = x.max()+offset
ymin = y.min()-offset
ymax = y.max()+offset

X, Y = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
positions = np.vstack([X.ravel(), Y.ravel()])
values = np.vstack([x, y])
kernel = sps.gaussian_kde(values, weights=z)
Z = np.reshape(kernel(positions).T, X.shape)

fig, ax = plt.subplots(figsize=(7, 7))
ax.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r,
          extent=[xmin, xmax, ymin, ymax],
          aspect='auto'
         )

sns.scatterplot(
    data=df,
    x='Hidden layer #1 size', y='Hidden layer #2 size',
    size='Average Hyper Loss', sizes=(5, 300),
    color='k'
)
ax.set_xlim([xmin, xmax])
ax.set_ylim([ymin, ymax])
#ax.legend(loc='upper left', bbox_to_anchor=(1,1))
plt.title('Hyperopt scan with 1 replica and theory id 200')
ax.set_xlabel('# of units Layer 1')
ax.set_ylabel('# of units Layer 2')

# Create a circle object at the best # of units
min_circle_center = (hyperopt_res[0], hyperopt_res[1])  # Replace x_value and y_value with your desired center coordinates
min_circle_radius = 1.0
min_circle = patches.Circle(min_circle_center, min_circle_radius, fill=False, color='red', linestyle='-', linewidth=3)
ax.add_patch(min_circle)
# Add a label (text annotation) near the circle
label_text = "Min" # 10 replicas"
label_x, label_y = min_circle_center[0] + min_circle_radius + 1, min_circle_center[1]  # Adjust the label position as needed
ax.annotate(label_text, (label_x, label_y), color='red', fontsize=12)

# Compare with the previous result
compare_circle_center = (25, 20)
compare_circle_radius = 1.0
compare_circle = patches.Circle(compare_circle_center, compare_circle_radius, fill=False, color='blue', linestyle='-', linewidth=3, label='Circle 2')
#ax.add_patch(compare_circle)
label_text = "Min 1 replica"
label_x, label_y = compare_circle_center[0] + compare_circle_radius + 1, compare_circle_center[1]  # Adjust the label position as needed
#ax.annotate(label_text, (label_x, label_y), color='blue', fontsize=12)

#plt.show()
fig.savefig('hyperopt_contour_1_replica.png')
#fig.savefig('hyperopt_contour_10_replicas.png')
