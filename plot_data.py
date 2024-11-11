import pandas as pd
import matplotlib.pyplot as plt
import os

# Show plot before saving?
showPlot = False
plotPath = "Plots"

# Load the CSV file
data = pd.read_csv('best_agent_per_evo.csv')  # Replace 'your_file.csv' with the actual file path

# Define the maximum generation number to plot
max_generation = 100  # Change this to the desired generation limit

# Filter data up to the specified generation
max_generation = min(max_generation, data['Generation'].max())
filtered_data = data[data['Generation'] <= max_generation]

# Plot Best Fitness, Position X, and Position Y over Generations up to max_generation
plt.figure(figsize=(10, 6))
plt.plot(filtered_data['Generation'], filtered_data['Best Fitness'], label='Best Fitness', color='red')
plt.plot(filtered_data['Generation'], filtered_data['Position X'], label='Position X', color='blue')
plt.plot(filtered_data['Generation'], filtered_data['Position Y'], label='Position Y', color='green')

# Adding labels and title
plt.xlabel('Generation')
plt.ylabel('Value')
plt.title('Best Fitness, Position X, and Position Y Over Generations')
plt.legend()

# Save plot
if not os.path.exists(plotPath):
    os.mkdir(plotPath)
pltName = input("Enter plot name: ")
if not pltName.endswith(".png"):
    pltName += ".png"
plt.savefig(plotPath + "/" + pltName)

# Show plot
if showPlot:
    plt.show()
