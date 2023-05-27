import sys

first_line = []
starting_points_for_edges = []
ending_points_for_edges = []
weights = []


def extract_values(line, largeFile):
    index_open_brac = line.index("[")
    index_close_brac = line.index("]")
    line = line[index_open_brac + 1:index_close_brac]
    if largeFile:
        return line.split(", ")
    else:
        return line.split(",")


def parse_file(instance, large_file):
    with open(instance, 'r') as file:
        line = file.readline()

        while line:
            if line.startswith("%"):
                line = file.readline()
                continue

            if line.__contains__("N = ") | line.__contains__("M = ") | \
                    line.startswith("Start = ") | line.startswith("End = "):
                index_equal = line.index("=")
                index_dot_comma = line.index(";")
                first_line.append(line[index_equal + 2:index_dot_comma])
                print(first_line)

            if line.__contains__("Edge_Start "):
                starting_points_for_edges = extract_values(line, large_file)
                print(starting_points_for_edges)

            if line.__contains__("Edge_End "):
                ending_points_for_edges = extract_values(line, large_file)
                print(ending_points_for_edges)

            if line.__contains__("L = "):
                weights = extract_values(line, large_file)
                print(weights)

            line = file.readline()
        return starting_points_for_edges, ending_points_for_edges, weights


def compose_new_file(file_path):
    # file_path = "SP_Instance1-data-txt.txt"
    with open(file_path, 'w') as file:
        # Write content to the file
        file.writelines(first_line[0] + " " + first_line[1] + " " + first_line[2] + " " +
                        first_line[3] + "\n")
        print(starting_points_for_edges)
        for i in range(0, len(starting_points_for_edges)):
            edge = starting_points_for_edges[i] + " " + ending_points_for_edges[i] + " " + weights[i] + "\n"
            print(edge)
            file.writelines(edge)

    print("File created and written successfully.")


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
        file_to_be_translated = str(args[1])

        # Files with larger numbers have spaces between the values in the lists
        if int(file_to_be_translated[len("data/FRCSP_instance_"): len(file_to_be_translated) - 4]) > 7:
            large_file = True
        else:
            large_file = False

        starting_points_for_edges, ending_points_for_edges, weights = parse_file(file_to_be_translated, large_file)

        # Specify the path and name of the new file
        new_file = file_to_be_translated[len("data/FRC"): len(file_to_be_translated) - 4] + "-sat.txt"
        new_file = "data-txt/" + new_file
        compose_new_file(new_file)
