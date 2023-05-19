from time_graph import parse_graph_with_time
import sys

def run(graph):
    pass

def main(file_name):
    with open(file_name, 'r') as graph_file:
        graph = parse_graph_with_time(graph_file.read())

if __name__ == "__main__":
    main(sys.argv[len(sys.argv)- 1])