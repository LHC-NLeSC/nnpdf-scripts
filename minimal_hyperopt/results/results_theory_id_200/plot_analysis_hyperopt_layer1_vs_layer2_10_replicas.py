import json
from typing import Tuple, List
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import seaborn as sns
import scipy.interpolate as interp


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

    #print(data[52])

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


# path to 'tries.json' file
path_to_file = 'hyperopt_10_rep_1000_trials_8_Sep_2023/nnfit/replica_1/tries.json'

# number of Trials
n_trials = 70

df, hyperopt_res = filter_data(path_to_file, n_trials)

#print(df)

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
xmin = 10-offset  # x.min()-offset
xmax = 45+offset  # x.max()+offset
ymin = 10-offset  # y.min()-offset
ymax = 45+offset  # y.max()+offset

# Create a grid of points for the contour plot
X, Y = np.meshgrid(np.linspace(xmin, xmax, 500), np.linspace(ymin, ymax, 500))

# Evaluate the z values at each point on the grid using interpolation
Z = interp.griddata((x, y), z, (X, Y), method='cubic')

# Create the contour plot
fig, ax = plt.subplots(figsize=(7, 7))
contour = ax.contourf(X, Y, Z, cmap=plt.cm.gist_earth_r)
plt.colorbar(contour)  # Add a colorbar to the plot

# Optionally, you can add labels and titles to the plot
ax.set_xlabel('# of units hidden layer 1')
ax.set_ylabel('# of units hidden layer 2')
ax.set_title('Contour Plot of Average Hyper Loss: 10 replicas & theory 200')

sns.scatterplot(
    data=df,
    x='Hidden layer #1 size', y='Hidden layer #2 size',
    size='Average Hyper Loss', sizes=(5, 300),
    color='k',
    legend=False
)
ax.set_xlim([xmin, xmax])
ax.set_ylim([ymin, ymax])

# Create a circle object at the best # of units
min_circle_center = (hyperopt_res[0], hyperopt_res[1])
min_circle_radius = 1.0
min_circle = patches.Circle(min_circle_center, min_circle_radius, fill=False, color='red', linestyle='-', linewidth=3)
ax.add_patch(min_circle)
# Add a label (text annotation) near the circle
label_text = "Min" # 10 replicas"
label_x, label_y = min_circle_center[0] + min_circle_radius + 1, min_circle_center[1]  # Adjust the label position as needed
ax.annotate(label_text, (label_x, label_y), color='red', fontsize=12)

# Compare with the previous result
# Add a star at the point (25, 20)
star_x, star_y = 25, 20
ax.scatter(star_x, star_y, marker='*', color='red', s=200, label='Point (25, 20)')

#plt.show()
fig.savefig('hyperopt_contour_10_replicas.png')