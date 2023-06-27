import sys
import glob
import os
from time import sleep
import numpy as np
import csv
from datetime import datetime


def run_model(model_file = "View2.mzn", data_file = "Example1.dzn", solver = "Chuffed", VERBOSE = False):

    command = f'minizinc --output-time --solver {solver} --time-limit 60000 "{model_file}" {data_file}'
    if VERBOSE:
        print(f"Running: {command}")
    start = datetime.now()
    stream = os.popen(command)
    end = datetime.now()
    try:
        output = stream.read()
    except KeyboardInterrupt:
        sleep(2)
        print("Got KeyBoardInterrupt")
        return "*** Interrupted ***", None
    time = None
    print(output)
    lines = output.split("\n")
    if(lines[-1].startswith("% time elapsed:")):
        time = float(lines[-1].split(" ")[3])
    elif len(lines) >= 2:
        if lines[-2].startswith("% time elapsed:"):
            time = float(lines[-2].split(" ")[3])
    elif len(lines) >= 3:
        if lines[-3].startswith("% time elapsed:"):
            time = float(lines[-3].split(" ")[3])
    return output,time

def write_output_to_file(filename,output):
    with open(filename, 'w') as f:
        f.write(output)

def main(problem):
    problem = str(problem)
    upper = np.core.defchararray.swapcase(problem)
    output_folder = "output_sat/"
    path = f"data/{problem}/*.dzn"
    models = glob.glob(f"{upper}*.mzn")
    solvers = ["Gecode"]
    #start creating the csv
    first_row = ["Instance"] + [s for s in solvers for i in range(1,len(models) + 1)]
    second_row = [""] + [m.replace(".mzn","") for i in range(1,len(solvers) + 1) for m in models]
    result_csv = [first_row,second_row]
    #write first two rows
    result_csv_file = f'output-{problem}.csv'
    with open(result_csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(first_row)
        writer.writerow(second_row)
    for data_file in glob.glob(path):
        print(data_file)
        row = [data_file.replace("data_bs/","").replace(".dzn","")]
        for solver in solvers:
            for model in models:
                print(f"Running {model} on {data_file} with {solver}")
                total_output = ""
                total_time = []
                for run in np.arange(1,3):
                    print(f"Run #{run}")
                    output,time = run_model(model_file = model, data_file = data_file,solver = solver, VERBOSE=True)
                    total_output += output
                    total_time.append(time)
                    if time == None:
                        break
                if len(total_time) == 0:
                    average_time = None
                elif total_time[0] == None:
                    average_time = None
                else:
                    average_time = np.mean(total_time)
                row.append(str(average_time).replace("None","t\o"))
                total_output += "Average time: " + str(average_time)
                output_file = output_folder + solver + "/" + model.replace(".mzn","") + "_" + data_file.replace(f"data/{problem}/","").replace(".dzn",".") + ".txt"
                #write intermediate output for debud purposes results for debug
                write_output_to_file(output_file,total_output)
        result_csv.append(row)
        with open(result_csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)


    write_output_to_file("output.txt",str(result_csv))

if __name__ == "__main__":
    main(sys.argv[1])

