import sys
# from pysat.solvers import Glucose3, Solver
from pysat.pb import *
from pysat.formula import WCNFPlus
from pysat.examples.fm import FM
from pysat.formula import IDPool
from time import time

incoming_edges = []
outgoing_edges = []
neighbours = []
task_sets = []
wcnf = WCNFPlus()
vpool = IDPool()


def read_problem(type, file) -> (int, int, int):
    if (type != 'node') & (type != 'ordered_task') & (type != 'unordered_task') & (type != 'SP'):
        print("The following program tackles only node CSP and unordered/ordered task CSP, and SP!")
        return

    with open(file, 'r') as file:
        line = file.readline()

        # first line num of vertices and edges and ...
        first_line = line.split(' ')
        counter_tasks_nodes = 0
        if type != "SP":
            if len(first_line) != 5:
                print("The number of arguments on the first line is not correct")
                print("First line: #vertices #edges source destination #task sets/#nodes with penalties")
                return
            num_tasks_or_nodes = int(first_line[4])  # depending whether task or node with penalties is run
        else:
            if len(first_line) != 4:
                print("The number of arguments on the first line is not correct")
                print("First line: #vertices #edges source destination")
                return

        num_vertices = int(first_line[0])
        num_edges = int(first_line[1])
        source = int(first_line[2])
        destination = int(first_line[3])

        # create empty list of lists for the neighbouring edges and neighbours for each node
        for i in range(0, int(num_vertices) + 1):  # first list will be empty
            incoming_edges.append([])
            outgoing_edges.append([])
            neighbours.append([])
            if i != 0:
                vpool.id(i)  # assign each node an id (it will be the same as the node number)

        line = file.readline()
        counter_edges = 1
        while line:
            # Split the line into separate components using spaces as the delimiter
            elements = line.split(' ')

            # Convert elements to integers
            int_elements = [int(element) for element in elements]

            if counter_edges <= num_edges:
                counter_edges += 1

                # Create edge encoding
                edge = int(elements[0] + elements[1])

                # Add neighbouring edges
                outgoing_edges[vpool.id(int_elements[0])].append(vpool.id(edge))
                incoming_edges[vpool.id(int_elements[1])].append(vpool.id(edge))

                # Add neighbours
                neighbours[vpool.id(int_elements[0])].append(vpool.id(int_elements[1]))  # outgoing neighbours

                # append soft constraint to wcnf
                # when the edge is picked edge == 1,
                # then we accumulate a cost of weight
                wcnf.append([-vpool.id(edge)], weight=int_elements[2])

            else:
                # we have read all edges
                if type == "SP":
                    print(f"The file has more edges than specified on the first line,"
                          f" the first {num_edges} edges will be read")
                elif type == 'node':
                    # Add a soft clause for each node and its penalty
                    wcnf.append([-vpool.id(int_elements[0])], weight=int_elements[1])
                    counter_tasks_nodes += 1
                    break
                else:
                    # (un)ordered task
                    id_int_elements = [vpool.id(element) for element in int_elements]  # convert nodes to their node ids
                    if counter_tasks_nodes < num_tasks_or_nodes:
                        # it is a task constraint
                        wcnf.append(id_int_elements)  # pass through at least one of those nodes
                        task_sets.append(id_int_elements)
                        counter_tasks_nodes += 1

                if counter_tasks_nodes == num_tasks_or_nodes:
                    break
            line = file.readline()

        return num_vertices, source, destination


def source_destination_constraints(source, destination):
    # Source and destination constraints
    id_source = vpool.id(source)
    id_destination = vpool.id(destination)
    wcnf.append([id_source])  # source and destination nodes should be part of the path
    wcnf.append([id_destination])

    # the sum of all neighbouring edges of the source/destination should be 1, only 1 edge should be in the path
    if not outgoing_edges[id_source]:
        return "There are no outgoing edges from the source! No possible path from source to destination"

    wcnf.extend(PBEnc.equals(lits=outgoing_edges[id_source], bound=1))
    if incoming_edges[id_source]:
        wcnf.extend(PBEnc.equals(lits=incoming_edges[id_source], bound=0))

    if not incoming_edges[id_destination]:  # add a constraint only if list of neighbours are non-empty
        return "There are no incoming edge for the destination! No possible path from source to destination"

    wcnf.extend(PBEnc.equals(lits=incoming_edges[id_destination], bound=1))
    if outgoing_edges[id_destination]:
        wcnf.extend(PBEnc.equals(lits=outgoing_edges[id_destination], bound=0))


def add_constraints(num_vertices, source, destination):
    # Create hard constraints

    # Source and destination constraints
    source_destination_constraints(source, destination)

    # Other nodes constraints
    for i in range(1, num_vertices + 1):
        if (i != source) & (i != destination):
            id_i = vpool.id(i)
            weights_out = [1] * (len(outgoing_edges[id_i]) + 1)  # the weights of the vertex in -A + outgoing edges = 1
            weights_in = [1] * (len(incoming_edges[id_i]) + 1)

            outgoing_edges[id_i].append(-id_i)  # add the node to the constraint -A
            incoming_edges[id_i].append(-id_i)

            wcnf.extend(PBEnc.equals(lits=outgoing_edges[id_i], weights=weights_out, vpool=vpool, bound=1))
            wcnf.extend(PBEnc.equals(lits=incoming_edges[id_i], weights=weights_in, vpool=vpool, bound=1))
            outgoing_edges[id_i].pop()
            incoming_edges[id_i].pop()

    # Additional specific constraints
    # Task path constraints
    if type == 'ordered_task':
        forbid_incorrect_task_paths(task_sets, source)


def forbid_incorrect_task_paths(task_sets, source):
    if len(task_sets) == 1:
        return  # we don't need to enforce additional constraints

    # generate all possible paths from the source to the second task set and forbid those
    nieghbours_per_vertex = neighbours[vpool.id(source)]
    forbidden_path = []
    forbid_path_per_node(forbidden_path, 1, nieghbours_per_vertex, task_sets,
                         source)  # any connection to node from different set
    # then the 0th one should be forbidden
    set_num = 0
    print(task_sets[set_num])
    for id_node in task_sets[set_num]:
        if set_num + 2 < len(task_sets):
            id_of_nieghbours_per_vertex = neighbours[id_node]
            forbidden_path = []
            forbid_path_per_node(forbidden_path, set_num + 2, id_of_nieghbours_per_vertex, task_sets, id_node)
        else:
            break  # there is nothing else to be checked
        set_num += 1


def forbid_path_per_node(forbidden_path, check_sets_from, id_of_nieghbours_per_vertex, task_sets, id_start_node):
    for id_neighbour in id_of_nieghbours_per_vertex:
        task_sets_counter = check_sets_from
        part_of_set = False

        if id_neighbour in task_sets[task_sets_counter - 1]:
            continue

        while task_sets_counter < len(task_sets):  # num_task_sets
            # check whether the neighbour is contained in any of the task sets
            if id_neighbour in task_sets[task_sets_counter]:
                part_of_set = True
                # forbid this directed edge (path)
                forbidden_path.append(vpool.id(int(str(id_start_node) + str(id_neighbour))) * (-1))
                wcnf.append(forbidden_path)
                forbidden_path.pop()
                break
            task_sets_counter += 1

        if not part_of_set:
            if id_neighbour not in forbidden_path:
                print(forbidden_path)
                forbidden_path.append(id_neighbour)
                forbid_path_per_node(forbidden_path, check_sets_from, neighbours[id_neighbour], task_sets, id_neighbour)
                forbidden_path.pop()


def run(file, type, solver):
    try:
        num_vertices, source, destination = read_problem(type, file)
    except Exception as err:
        return "Input arguments on first line are incorrect " + str(err)

    # print("Task sets are " + str(task_sets))
    add_constraints(num_vertices, source, destination)

    # solve the model
    fm = FM(wcnf, solver=solver, verbose=0)

    start_time = time()
    if fm.compute():  # set of hard clauses should be satisfiable
        print("The variables are assigned the following values " + str(fm.model))
        print("The length of the CSP is " + str(fm.cost))
    else:
        print("The instance is unsatisfiable")

    print(f"solveTime={time() - start_time}")


if __name__ == '__main__':
    args = sys.argv

    # Check the number of arguments provided
    num_args = len(args)

    # Access individual arguments
    if num_args > 4:
        print("Atmost 3 parameters: the name of the instance, the type - node, ordered_task, or unordered_task"
              ", and the type of solver!")
    elif num_args <= 1:
        print("Provide the type of problem that you run. This could be 'node' or 'type' CSP.")
    else:
        file = str(args[1])
        type = str(args[2])
        if num_args > 3:
            solver = str(args[3])
        else:
            solver = 'cadical153'
        output = run(file, type, solver)
        if output is not None:
            print(output)
