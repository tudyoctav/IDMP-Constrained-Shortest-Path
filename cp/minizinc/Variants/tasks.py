import numpy as np


def shuffle(nodes, tasks, nodes_per_task):
    positions = []
    for t in range(tasks):
        positions = positions + list(np.full(nodes_per_task, t + 1))
    positions = positions + list(np.zeros(nodes - len(positions)))
    np.random.shuffle(positions)
    return positions


def generate_tasks(nodes, tasks, nodes_per_task):
    positions = shuffle(nodes, tasks, nodes_per_task)

    output = f"array2d(1..tasks, 1..nodes, ["
    for t in range(1,tasks+1):
        output = output + "\n"
        for n in range(1,nodes+1):
            if int(positions[n-1]) == t:
                output = output + str(1)
            else:
                output = output + str(0)
            if not (t == tasks and n == nodes):
                output = output + ", "
            else:
                output = output + "]);"

    print(output + f"\nOutput generated for: {nodes} nodes {tasks} x {nodes_per_task}")


def generate_int_tasks(nodes, tasks, nodes_per_task):
    positions = shuffle(nodes, tasks, nodes_per_task)

    output = "["
    for i, p in enumerate(positions):
        if i+1 != len(positions):
            output = output + str(int(p)) + ","
        else:
            output = output + str(int(p)) + "]"

    print(output)


def bool_to_int(ones, twos, threes):
    ar1 = np.array(ones)

    ar2 = np.array(twos)
    ar2 = np.where(ar2 == 1, 2, ar2)

    ar3 = np.array(threes)
    ar3 = np.where(ar3 == 1, 3, ar3)

    res = np.add(ar1, np.add(ar2, ar3))

    output = "["
    for i, p in enumerate(res):
        if i+1 != len(res):
            output = output + str(p) + ","
        else:
            output = output + str(p) + "]"

    print(output)


generate_tasks(256, 4, 15)
