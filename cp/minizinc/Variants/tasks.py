import numpy as np

def generate_tasks(tasks, nodes, nodes_per_task):
    positions = []
    for t in range(tasks):
        positions = positions + list(np.full(nodes_per_task, t+1))
    positions = positions + list(np.zeros(nodes-len(positions)))
    np.random.shuffle(positions)

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

    print(output)


generate_tasks(3, 128, 3)