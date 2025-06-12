from .ClusterMerger import plot_clusters_with_flow, merge_all_within_threshold, classesToClusterDictionary
from .PointClassifier import classify_points_latest_only, drop_clusters_with_low_number_of_points
from .trilateration import calculateListOfPoints
from PIL import Image
import sys
import math
import copy
import csv

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from collections import Counter

class Area:
    def __init__(self, name, point1, point2):
        self.name = name
        # Normalize the rectangle (ensure point1 is bottom-left, point2 is top-right)
        self.x_min = min(point1[0], point2[0])
        self.x_max = max(point1[0], point2[0])
        self.y_min = min(point1[1], point2[1])
        self.y_max = max(point1[1], point2[1])

    def contains(self, point):
        x, y = point
        return self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max

def find_area_for_point(point, areas):
    for area in areas:
        if area.contains(point):
            return area.name
    return "Moving"
def readPointsFromCSV(filename):
    xyPoints = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        
        # If your CSVs have headers like "x,y", uncomment the next line:
        # next(reader, None)  # skip header row
        next(reader, None)

        for row in reader:
            # Each row is expected to have two columns: x, y
            if len(row) < 2:
                continue
            x_val, y_val = float(row[0]), float(row[1])
            xyPoints.append((x_val,y_val))
    return xyPoints
def transformPointDataFromAnyLogicSimulation(points , imageXzero = 35 , imageYzero = 36 , inverseY = True):
    newPoints = []
    if points != None:
        for i in range(0,len(points)):
            newX = points[i][0]- imageXzero
            newY = imageYzero - points[i][1]
            newPoints.append((newX, newY))
    return newPoints
def seconds_to_hm(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    if h > 0:
        return f"{h}h:{m}m"
    elif m > 0:
        return f"{m}m"
    else:
        return f"{seconds}s"
def summarize_states(states, interval_seconds):
    if not states:
        return []

    result = []
    current_state = states[0]
    start_index = 0

    for i in range(1, len(states)):
        if states[i] != current_state:
            result.append((start_index * interval_seconds, current_state))
            current_state = states[i]
            start_index = i

    # Append the last state
    result.append((start_index * interval_seconds, current_state))
    return result
def state_to_numeric(states):
    unique_states = sorted(set(state for _, state in states))
    state_map = {state: i for i, state in enumerate(unique_states)}
    numeric_states = [(t, state_map[state]) for t, state in states]
    return numeric_states, state_map

def plot_step_states(states_summary):
    numeric_states, state_map = state_to_numeric(states_summary)

    times = [t for t, _ in numeric_states]
    values = [v for _, v in numeric_states]

    if len(times) > 1:
        end_time = (times[-1] + (times[-1] - times[-2]))
    else:
        end_time = times[-1] + 1
    times.append(end_time)
    values.append(values[-1])

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.step(times, values, where='post', linewidth=2)

    ax.set_yticks(list(state_map.values()))
    ax.set_yticklabels(list(state_map.keys()))
    ax.set_ylabel("State")
    ax.set_xlabel("Time")

    # Format x-axis labels as hours and minutes
    def time_formatter(x, pos):
        return seconds_to_hm(int(x))

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(time_formatter))
    ax.set_title("State Transitions Over Time")
    ax.grid(True)
    plt.tight_layout()
    plt.show()
def calculateUtilization( states, idleStateName = "IDLE"):
    print( "Utilization:", 1 - states.count(idleStateName)/len(states))
def utilizationGraph(states, sumPeriod = 3600, idleStateName = "IDLE"):
    avgUtil = []
    xAxisValues = []
    for i in range (sumPeriod, len(states), sumPeriod):
        sum = 0
        end = min(i, len(states))
        for j in range(0, end):
            if (states[j] == idleStateName):
                sum = sum + 1
        avgUtil.append(1 - sum/end)
        xAxisValues.append(seconds_to_hm(i))
    return avgUtil, xAxisValues, Counter(states)
def main():
    # Example setup:
    areas_data = [
        ("Output Racks", (18, 16), (38, 23)),
        ("Input Racks", (18, 2), (38, 9)),
        ("Unloading Truck", (1, 5), (7, 13)),
        ("Loading Truck", (1, 17), (7, 23)),
        ("IDLE", (37, 9), (42, 16)),
        ("Machine", (45, 5), (50, 20))
    ]
    
    input_file = "C:\\Users\\thano\\OneDrive - Αριστοτέλειο Πανεπιστήμιο Θεσσαλονίκης\\PhD Dissertation\\Job Shop1 with Positioning Data\\population3.csv"
    
    points = readPointsFromCSV(input_file)
    points = transformPointDataFromAnyLogicSimulation(points, imageXzero=35, imageYzero=36)

    # Create Area objects
    areas = [Area(name, p1, p2) for name, p1, p2 in areas_data]

    # Process points
    x = []
    y = []
    for idx, point in enumerate(points):
        area_name = find_area_for_point(point, areas)
        print(f"Point {idx} at {point} is in area: {area_name}")
        x.append(idx)
        y.append(area_name)

    calculateUtilization(y)
    stateTransitions = summarize_states(y, 1)
    utilValues, xValues, counterList = utilizationGraph(y, sumPeriod = 60)
    print(counterList)
    plot_step_states(stateTransitions)
    
    fig, ax = plt.subplots()
    ax.plot(range(len(xValues)), utilValues, marker='o', linestyle='-', color='b')  # Plot using integer indices

    # Set x-ticks at every 100th position
    ax.set_xticks(range(0, len(xValues), 20))
    ax.set_xticklabels(xValues[::20], rotation=45, ha='right')

    ax.set_title('Forklift Utilization')
    ax.set_xlabel('Time')
    ax.set_ylabel('Overall Utilization')
    ax.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()