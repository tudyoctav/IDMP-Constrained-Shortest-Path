import time_window_main
import resource_constrained_main
import sys

if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) == 3:
        if sys.argv[1] == 'resource_constraint':
            resource_constrained_main.main(sys.argv[2])
            sys.exit()
        elif sys.argv[1] == 'resource_constraint':
            resource_constrained_main.main(sys.argv[2])
            sys.exit()
    print("Error parsing input")
    print(f"Usage: '{sys.executable}' '{sys.argv[0]}' PROBLEM FILE_TO_RUN")
    print("Possible problmes: 'resource_constraint', 'time_window'")
    print("Supported files: '*.dzn', '*.txt'")
    sys.exit(1)