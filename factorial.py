import time
import numpy as np
import matplotlib
matplotlib.use('TkAgg') # Interactive backend
import matplotlib.pyplot as plt

def time_complexity_visualizer(algorithm, n_min, n_max, n_step):
    time = []
    input_sizes = list(range(n_min, n_max + n_step, n_step))

    plt.ion() # Enable interaction mode
    fig, ax = plt.subplots()
    ax.set_xlabel('Input Size (n)')
    ax.set_ylabel('Running Time (seconds)')
    ax.set_title('Algorith time complexity visua;ization (Live)')
    line, = ax.plot([], [], 'o-')

    for i, n in enumerate(input_sizes):
        start_time = time.time()
        algorithm(n)
        end_time = time.time()

        elapsed_time = end_time - start_time
        time.append(elapsed_time)

        line.set_data(input_sizes[:i + 1], time)
        ax.relim()
        ax.autoscale_view()
        plt.draw()
        plt.pause(0.1) # Pause to update the plot

    plt.ioff() # Disable interaction mode
    plt.show()

def linear_search(n):
    for i in range(n):
