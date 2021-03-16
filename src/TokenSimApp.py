import matplotlib.pyplot as plt
import numpy as np
import matplotlib.collections as mcol
from matplotlib.legend_handler import HandlerLineCollection, HandlerTuple
from matplotlib.lines import Line2D
import tkinter as tk
import simpy
import TokenSimLib as tks
import random


def plotData(
    meanSystemArrayA,
    maxSystemArrayA,
    meanSystemArrayB,
    maxSystemArrayB,
    numberOfNodes,
    meanDictA,
    maxDictA,
    meanDictB,
    maxDictB,
):
    """
    Function to show the corresponding output.
    """
    load = np.arange(0, 110, 10)
    # System Data
    plt.figure(1)
    plt.subplot(1, 2, 1)
    (Line1,) = plt.plot(load, meanSystemArrayA, "b")
    (Line2,) = plt.plot(load, maxSystemArrayA, "r")
    plt.legend((Line1, Line2), ("Mean", "Max"), loc="upper left")
    plt.xlabel("Load (%)")
    plt.ylabel("System Delay (ms)")
    plt.title("A Class Messages")
    plt.grid()
    plt.subplot(1, 2, 2)
    (Line1,) = plt.plot(load, meanSystemArrayB, "b")
    (Line2,) = plt.plot(load, maxSystemArrayB, "r")
    plt.legend((Line1, Line2), ("Mean", "Max"), loc="upper left")
    plt.xlabel("Load (%)")
    plt.ylabel("System Delay (ms)")
    plt.title("B Class Messages")
    plt.grid()
    # Node Data
    plt.figure(2)
    for i in range(1, numberOfNodes + 1):
        plt.subplot(2, numberOfNodes, i)
        (Line1,) = plt.plot(load, meanDictA[i], "b")
        (Line2,) = plt.plot(load, maxDictA[i], "r")
        plt.legend((Line1, Line2), ("Mean", "Max"), loc="upper left")
        plt.xlabel("Load (%)")
        plt.ylabel("Node " + str(i) + " Delay (ms)")
        plt.title("A Class Messages")
        plt.grid()

        plt.subplot(2, numberOfNodes, numberOfNodes + i)
        (Line1,) = plt.plot(load, meanDictB[i], "b")
        (Line2,) = plt.plot(load, maxDictB[i], "r")
        plt.legend((Line1, Line2), ("Mean", "Max"), loc="upper left")
        plt.xlabel("Load (%)")
        plt.ylabel("Node " + str(i) + " Delay (ms)")
        plt.title("B Class Messages")
        plt.grid()
    plt.show()
    return 1


def runclick():
    """
    Run button handler. Creates and executes the simulations.
    """
    NumberOfNodes = int(entry_nodes.get())
    Ts = int(entry_Ts.get())
    Trt = int(entry_Trt.get())
    runtime = int(entry_Time.get())
    meanArrayA = [0]
    maxArrayA = [0]
    meanArrayB = [0]
    maxArrayB = [0]
    meanDictA = {}
    maxDictA = {}
    meanDictB = {}
    maxDictB = {}
    for i in range(1, NumberOfNodes + 1):
        meanDictA[i] = [0]
        maxDictA[i] = [0]
        meanDictB[i] = [0]
        maxDictB[i] = [0]
    for load in np.arange(0.1, 1.1, 0.1):
        # i = int(10 * load)
        env = simpy.Environment()
        bus = tks.Bus(env)
        token_address, nodes = tks.createNodes(NumberOfNodes, env, bus, load, Ts, Trt)
        bus.createToken(token_address)
        env.run(until=runtime)
        meanDictA, maxDictA, meanDictB, maxDictB = tks.report(
            nodes, meanDictA, maxDictA, meanDictB, maxDictB
        )
        SumA = SumB = MaxA = MaxB = 0
        for i in range(1, NumberOfNodes + 1):
            SumA += meanDictA[i][int(10 * load)]
            SumB += meanDictB[i][int(10 * load)]
            if maxDictA[i][int(10 * load)] > MaxA:
                MaxA = maxDictA[i][int(10 * load)]
            if maxDictB[i][int(10 * load)] > MaxB:
                MaxB = maxDictB[i][int(10 * load)]
        meanArrayA.append(SumA / NumberOfNodes)
        meanArrayB.append(SumB / NumberOfNodes)
        maxArrayA.append(MaxA)
        maxArrayB.append(MaxB)
    plotData(
        meanArrayA,
        maxArrayA,
        meanArrayB,
        maxArrayB,
        NumberOfNodes,
        meanDictA,
        maxDictA,
        meanDictB,
        maxDictB,
    )


##########################  main  #######################################

NumberOfNodes = 0
window = tk.Tk()
window.title("Token Bus Simulation")
window.resizable(False, False)
## Gui contents ##
label_nodes = tk.Label(window, text="Number of Nodes:")
entry_nodes = tk.Entry(window)
entry_nodes.insert(0, "10")
label_Ts = tk.Label(window, text="Ts (in μs):")
entry_Ts = tk.Entry(window)
entry_Ts.insert(0, "1000")
label_Trt = tk.Label(window, text="Trt (in μs):")
entry_Trt = tk.Entry(window)
entry_Trt.insert(0, "15000")
label_Time = tk.Label(window, text="Simulation Time (in μs):")
entry_Time = tk.Entry(window)
entry_Time.insert(0, "1000000")
button = tk.Button(window, text="Run", command=runclick)
## Content placement ##
label_nodes.grid(row=0, column=0)
entry_nodes.grid(row=0, column=1)
label_Ts.grid(row=1, column=0)
entry_Ts.grid(row=1, column=1)
label_Trt.grid(row=2, column=0)
entry_Trt.grid(row=2, column=1)
label_Time.grid(row=3, column=0)
entry_Time.grid(row=3, column=1)
button.grid(row=4, column=0, columnspan=2)
## mainloop ##
window.mainloop()
