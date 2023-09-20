import json
from typing import Tuple, List
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import seaborn as sns
import scipy.interpolate as interp


def filter_data(path_to_file: str, n_trials: int) -> Tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame, List
]:
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

    # print(data[1]) #['misc']['space_vals']['optimizer'])

    average_over_rep_and_k_hyper_losses = []
    hidden_layers_1 = []
    hidden_layers_2 = []
    optimizer_name = []
    optimizer_learning_rate = []
    optimizer_clipnorm = []
    trials = []

    for n in range(n_trials):

        # hyper loss averaged over replicas first and then over k-folds
        loss = data[n]['result']['loss']

        # attributes
        layer_size_1 = data[n]['misc']['space_vals']['nodes_per_layer'][0]
        layer_size_2 = data[n]['misc']['space_vals']['nodes_per_layer'][1]
        optimizer = data[n]['misc']['space_vals']['optimizer']['optimizer_name']
        learning_rate = data[n]['misc']['space_vals']['optimizer']['learning_rate']
        clipnorm = data[n]['misc']['space_vals']['optimizer']['clipnorm']

        # trial number
        trial_id = data[n]['tid']

        print(trial_id, optimizer, learning_rate, clipnorm)

        average_over_rep_and_k_hyper_losses.append(loss)
        hidden_layers_1.append(layer_size_1)
        hidden_layers_2.append(layer_size_2)
        optimizer_name.append(optimizer)
        optimizer_learning_rate.append(learning_rate)
        optimizer_clipnorm.append(clipnorm)
        trials.append(trial_id)

    # getting minimum values
    min_loss = min(average_over_rep_and_k_hyper_losses)
    min_loc = average_over_rep_and_k_hyper_losses.index(min_loss)
    min_layer_size_1 = hidden_layers_1[min_loc]
    min_layer_size_2 = hidden_layers_2[min_loc]
    min_optimizer_name = optimizer_name[min_loc]
    min_optimizer_learning_rate = optimizer_learning_rate[min_loc]
    min_optimizer_clipnorm = optimizer_clipnorm[min_loc]
    hyperopt_res = [
        min_layer_size_1, min_layer_size_2,
        min_optimizer_name, min_optimizer_learning_rate,
        min_optimizer_clipnorm, min_loss
    ]

    print("=================================================================")
    print(f"Minimum value of the hyper loss "
          f"(averaged over replicas and k-folds): {min_loss}")
    print(f"Optimum # of nodes per "
          f"layer: {min_layer_size_1, min_layer_size_2}")
    print(f"Optimal optimizer: {min_optimizer_name}, "
          f"learning rate: {min_optimizer_learning_rate}, "
          f"and clipnorm: {min_optimizer_clipnorm}")
    print(f"Optimum Trial #: {min_loc}")
    print(f"Total # of Trials: {n_trials}")
    print("=================================================================")


    # creating a DataFrames containing all data
    pd.set_option('display.float_format', '{:.16E}'.format)
    df = pd.DataFrame(
        {'Trial': trials,
         'Hidden layer #1 size': hidden_layers_1,
         'Hidden layer #2 size': hidden_layers_2,
         'Optimizer': optimizer_name,
         'Learning rate': optimizer_learning_rate,
         'Clipnorm': optimizer_clipnorm,
         'Average Hyper Loss': average_over_rep_and_k_hyper_losses}
    )

    # Replace 'inf' strings with NaN
    df = df.replace(float('inf'), pd.NA)

    # Drop rows containing NaN values in any column
    df = df.dropna(how='any')

    # Reset the index if needed
    df.reset_index(drop=True, inplace=True)

    # Create two separate DataFrames based on the 'Optimizer' column
    adam_df = df[df['Optimizer'] == 'Adam']
    nadam_df = df[df['Optimizer'] == 'Nadam']

    return df, adam_df, nadam_df, hyperopt_res


# path to 'tries.json' file
path_to_file = 'theory_400_hyperopt_1_rep_1000_trials_Sept_14/nnfit/replica_1/tries.json'

# number of Trials
n_trials = 160

df, adam_df, nadam_df, hyperopt_res = filter_data(path_to_file, n_trials)

print(df)
print(adam_df)
print(nadam_df)

# Contour 2D plot

offset = 0.25
xmin = 10 - offset
xmax = 45 + offset
ymin = 10 - offset
ymax = 45 + offset

# Create a grid of points for the contour plots
X, Y = np.meshgrid(np.linspace(xmin, xmax, 500), np.linspace(ymin, ymax, 500))

# Code for the top plot (centered)
x_top = df['Hidden layer #1 size']
y_top = df['Hidden layer #2 size']
z_top = df['Average Hyper Loss']

Z_top = interp.griddata((x_top, y_top), z_top, (X, Y), method='cubic')

# Create a 2x2 grid of subplots
fig, axs = plt.subplots(2, 2, figsize=(12, 10))

# Remove the top-right subplot
fig.delaxes(axs[0, 1])

# Define a position for the top subplot to center it
top_position = axs[0, 0].get_position()
top_position.x0 = 0.1  # Adjust as needed to center horizontally
top_position.x1 = 0.9  # Adjust as needed to center horizontally
top_position.y0 = 0.5  # Adjust as needed to center vertically
top_position.y1 = 1.0

# Set the position for the top subplot
axs[0, 0].set_position(top_position)

# Plot the top subplot (centered, spans two columns)
contour_top = axs[0, 0].contourf(X, Y, Z_top, cmap=plt.cm.gist_earth_r)
plt.colorbar(contour_top, ax=axs[0, 0])  # Add a colorbar to the top subplot

axs[0, 0].set_xlabel('# of units hidden layer 1')
axs[0, 0].set_ylabel('# of units hidden layer 2')
axs[0, 0].set_title('Contour Plot of Average Hyper Loss: 1 replica & theory 400')

sns.scatterplot(
    data=df,
    x='Hidden layer #1 size', y='Hidden layer #2 size',
    size='Average Hyper Loss', sizes=(5, 300),
    color='k',
    legend=False,
    ax=axs[0, 0]
)

axs[0, 0].set_xlim([xmin, xmax])
axs[0, 0].set_ylim([ymin, ymax])

# Create a circle object at the best # of units
min_circle_center = (hyperopt_res[0], hyperopt_res[1])
min_circle_radius = 1.0
min_circle = patches.Circle(min_circle_center, min_circle_radius, fill=False, color='red', linestyle='-', linewidth=3)
axs[0, 0].add_patch(min_circle)
# Add a label (text annotation) near the circle
label_text = "Min" # 10 replicas"
label_x, label_y = min_circle_center[0] + min_circle_radius + 1, min_circle_center[1]  # Adjust the label position as needed
axs[0, 0].annotate(label_text, (label_x, label_y), color='red', fontsize=12)

# Compare with the previous result
# Add a star at the point (25, 20)
star_x, star_y = 25, 20
axs[0, 0].scatter(star_x, star_y, marker='*', color='red', s=200, label='Point (25, 20)')

# Code for the left plot (bottom left)
x1 = adam_df['Hidden layer #1 size']
y1 = adam_df['Hidden layer #2 size']
z1 = adam_df['Average Hyper Loss']

X1, Y1 = np.meshgrid(np.linspace(xmin, xmax, 500), np.linspace(ymin, ymax, 500))
Z1 = interp.griddata((x1, y1), z1, (X1, Y1), method='cubic')

# Plot the bottom-left subplot
contour1 = axs[1, 0].contourf(X1, Y1, Z1, cmap=plt.cm.gist_earth_r)
plt.colorbar(contour1, ax=axs[1, 0])  # Add a colorbar to the bottom-left subplot

axs[1, 0].set_xlabel('# of units hidden layer 1')
axs[1, 0].set_ylabel('# of units hidden layer 2')
axs[1, 0].set_title('Adam')

sns.scatterplot(
    data=adam_df,
    x='Hidden layer #1 size', y='Hidden layer #2 size',
    size='Average Hyper Loss', sizes=(5, 300),
    color='k',
    legend=False,
    ax=axs[1, 0]
)

axs[1, 0].set_xlim([xmin, xmax])
axs[1, 0].set_ylim([ymin, ymax])

# Create a circle object at the best # of units
min_circle_center = (hyperopt_res[0], hyperopt_res[1])
min_circle_radius = 1.0
min_circle = patches.Circle(min_circle_center, min_circle_radius, fill=False, color='red', linestyle='-', linewidth=3)
axs[1, 0].add_patch(min_circle)
# Add a label (text annotation) near the circle
label_text = "Min" # 10 replicas"
label_x, label_y = min_circle_center[0] + min_circle_radius + 1, min_circle_center[1]  # Adjust the label position as needed
axs[1, 0].annotate(label_text, (label_x, label_y), color='red', fontsize=12)

# Compare with the previous result
# Add a star at the point (25, 20)
#star_x, star_y = 25, 20
#axs[1, 0].scatter(star_x, star_y, marker='*', color='red', s=200, label='Point (25, 20)')

# Code for the right plot (bottom right)
x2 = nadam_df['Hidden layer #1 size']
y2 = nadam_df['Hidden layer #2 size']
z2 = nadam_df['Average Hyper Loss']

X2, Y2 = np.meshgrid(np.linspace(xmin, xmax, 500), np.linspace(ymin, ymax, 500))
Z2 = interp.griddata((x2, y2), z2, (X2, Y2), method='cubic')

# Plot the bottom-right subplot
contour2 = axs[1, 1].contourf(X2, Y2, Z2, cmap=plt.cm.gist_earth_r)
plt.colorbar(contour2, ax=axs[1, 1])  # Add a colorbar to the bottom-right subplot

axs[1, 1].set_xlabel('# of units hidden layer 1')
axs[1, 1].set_ylabel('# of units hidden layer 2')
axs[1, 1].set_title('Nadam')

sns.scatterplot(
    data=nadam_df,
    x='Hidden layer #1 size', y='Hidden layer #2 size',
    size='Average Hyper Loss', sizes=(5, 300),
    color='k',
    legend=False,
    ax=axs[1, 1]
)

axs[1, 1].set_xlim([xmin, xmax])
axs[1, 1].set_ylim([ymin, ymax])

# Compare with the previous result
# Add a star at the point (25, 20)
#star_x, star_y = 25, 20
#axs[1, 1].scatter(star_x, star_y, marker='*', color='red', s=200, label='Point (25, 20)')

plt.tight_layout()  # Ensure subplots don't overlap
#plt.show()
fig.savefig('hyperopt_contour_1_replica.png')