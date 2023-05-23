import sys
from pysat.solvers import Glucose3, Solver
from pysat.pb import *
from pysat.formula import WCNFPlus
from pysat.examples.fm import FM


incoming_edges = []
outgoing_edges = []
neighbours = []
task_sets = []
wcnf = WCNFPlus()

def read_problem(type) -> (int, int, int):
    if (type != 'node') & (type != 'task'):
        print("The following program tackles only node CSP and task CSP!")
        return

    with open('simple_tests/simple_test_task.txt', 'r') as file:
        line = file.readline()

        # first line num of vertices and edges and ...
        first_line = line.split(' ')
        num_vertices = int(first_line[0])
        num_edges = int(first_line[1])
        source = int(first_line[2])
        destination = int(first_line[3])

        # if the problem is task CSP
        if type == 'task':
            counter_task_sets = 0
            try:
                num_task_sets = int(first_line[4]) # check that there is an element
            except Exception as err:
                return str(err)

        # create empty list of lists for the neighbouring edges and neighbours for each node
        for i in range(0, int(num_vertices) + 1): # first list will be empty
            incoming_edges.append([])
            outgoing_edges.append([])
            neighbours.append([]) # I think this is needed only if the problem is task CSP

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

                # print(edge)
                # Add neighbouring edges
                outgoing_edges[int_elements[0]].append(edge)
                incoming_edges[int_elements[1]].append(edge)
                # neighbouring_edges[int_elements[1]].append(edge) # if directed remove this, they should be directed for TCSP

                # Add neighbours
                neighbours[int_elements[0]].append(int_elements[1]) # outgoing neighbours
                # neighbours[int_elements[1]].append(int_elements[0])

                # append soft constraint to wcnf
                # when the edge is picked edge == 1,
                # then we accumulate a cost of weight
                wcnf.append([-edge], weight=int_elements[2])

            else:
                # we have read all edges
                # if it is node constraint
                if type == 'node':
                    # Add the mandatory nodes
                    wcnf.extend(PBEnc.equals(lits=int_elements, bound=len(int_elements)))
                    break
                else:
                    if counter_task_sets < num_task_sets:
                        # it is a task constraint
                        wcnf.append(int_elements) # pass through at least one of those nodes
                        task_sets.append(int_elements)
                        counter_task_sets += 1

            line = file.readline()
        # print("Hard constraints are " + str(wcnf.hard))
        # print("Soft constraints are " + str(wcnf.soft))
        return num_vertices, source, destination


def add_other_path_constraint(num_vertices, source, destination):
    # Create hard constraints

    # Source and destination constraints
    wcnf.append([source]) # source and destination nodes should be part of the path
    wcnf.append([destination])

    # the sum of all neighbouring edges of the source/destination should be 1, only 1 edge should be in the path
    if not outgoing_edges[source]:
        return "There are no outgoing edges from the source! No possible path from source to destination"

    wcnf.extend(PBEnc.equals(lits=outgoing_edges[source], bound=1))
    if incoming_edges[source]:
        wcnf.extend(PBEnc.equals(lits=incoming_edges[source], bound=0))

    if not incoming_edges[destination]: # add a constraint only if list of neighbours are non-empty
        return "There are no incoming edge for the destination! No possible path from source to destination"

    wcnf.extend(PBEnc.equals(lits=incoming_edges[destination], bound=1))
    if outgoing_edges[destination]:
        wcnf.extend(PBEnc.equals(lits=outgoing_edges[destination], bound=0))

    # print("After adding source and destination constraints, hard constraints are " + str(wcnf.hard))
    # print("After adding source and destination constraints, soft constraints are " + str(wcnf.soft))

    # Other nodes constraints
    for i in range(1, num_vertices + 1):
        if (i != source) & (i != destination):
            weights_out = [1] * (len(outgoing_edges[i]) + 1) # the weights of the vertex in -A + outgoing edges = 1
            weights_in = [1] * (len(incoming_edges[i]) + 1)

            # print(str(i) + "outgoing are " + str(outgoing_edges[i]) + "incoming are " + str(incoming_edges[i]))
            # if neighbouring_edges[i]:
            outgoing_edges[i].append(-i)  # add the node to the constraint -A
            incoming_edges[i].append(-i)
            wcnf.extend(PBEnc.equals(lits=outgoing_edges[i],weights=weights_out, bound=1))
            wcnf.extend(PBEnc.equals(lits=incoming_edges[i], weights=weights_in, bound=1))
            outgoing_edges[i].pop()
            incoming_edges[i].pop()
    # print("After other nodes constraints, hard constraints are " + str(wcnf.hard))
    # print("After other nodes constraints, soft constraints are " + str(wcnf.soft))

    # Additional specific constraints
    # Task path constraints
    if type == 'task':
        print(task_sets)
        forbid_incorrect_task_paths(task_sets, source)


def forbid_incorrect_task_paths(task_sets, source):
    if len(task_sets) == 1:
        return # we don't need to enforce additional constraints

    # generate all possible paths from the source to the second task set and forbid those
    nieghbours_per_vertex = neighbours[source]
    forbidden_path = []
    forbid_path_per_node(forbidden_path, 1,  nieghbours_per_vertex, task_sets, source) # any connection to node from different set
    # then the 0th one should be forbidden
    set_num = 0
    print(task_sets[set_num])
    for vertex in task_sets[set_num]:
        if set_num + 2 < len(task_sets):
            nieghbours_per_vertex = neighbours[vertex]
            forbidden_path = []
            forbid_path_per_node(forbidden_path, set_num + 2, nieghbours_per_vertex, task_sets, vertex)
        else:
            break # there is nothing else to be checked
        set_num += 1


def forbid_path_per_node(forbidden_path, check_sets_from, nieghbours_per_vertex, task_sets, start_node):
    for neighbour in nieghbours_per_vertex:
        task_sets_counter = check_sets_from
        part_of_set = False

        if neighbour in task_sets[task_sets_counter - 1]:
            continue

        while task_sets_counter < len(task_sets): # num_task_sets
            # check whether the neighbour is contained in any of the task sets
            if neighbour in task_sets[task_sets_counter]:
                part_of_set = True
                # forbid this directed edge (path)
                forbidden_path.append(int(str(start_node) + str(neighbour)) * (-1))
                wcnf.append(forbidden_path)
                forbidden_path.pop()
                # break the while loop (assumption if the node is in one of the sets then it won't be in the others)
                break
            task_sets_counter += 1

        if not part_of_set:
            forbidden_path.append(neighbour)
            forbid_path_per_node(forbidden_path, check_sets_from, neighbours[neighbour], task_sets, neighbour)
            forbidden_path.pop()


if __name__ == '__main__':
    args = sys.argv

    # Check the number of arguments provided
    num_args = len(args)

    # Access individual arguments
    if num_args > 2:
        print("This program expects only one parameter!")
    elif num_args <= 1:
        print("Provide the type of problem that you run. This could be 'node' or 'type' CSP.")
    else:
        type = str(args[1])
        num_vertices, source, destination = read_problem(type)
        print("Task sets are " + str(task_sets))
        add_other_path_constraint(num_vertices, source, destination)

        # solve the model
        fm = FM(wcnf, verbose=0)

        print("Hard constraints are " + str(wcnf.hard))
        print("Soft constraints are " + str(wcnf.soft))
        if fm.compute():  # set of hard clauses should be satisfiable
            print("The instance is satisfiable")
            print("The variables are assigned the following values " + str(fm.model))
            print("The length of the CSP is " + str(fm.cost))
        else:
            print("The instance is unsatisfiable")

