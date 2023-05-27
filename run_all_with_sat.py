import sys
import glob
import os
from time import sleep
import numpy as np
import csv
from datetime import datetime
import subprocess


def run_command(command, VERBOSE):
    if VERBOSE:
        print(f"Running: {command}")
    start = datetime.now()
    # stream = os.popen(command)
    end = datetime.now()
    try:
        # output = stream.read()
        output = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,  shell=True, text=True)
        try:
            output.wait(timeout=50)
        except subprocess.TimeoutExpired:
            return "*** Timeout ***", None
    except KeyboardInterrupt:
        sleep(2)
        print("Got KeyBoardIntrerup")
        return "*** Interrupted ***", None
    time = None
    # print(output.stdout.read())
    lines = output.stdout.read()
    if(lines[-1].startswith("% time elapsed:")):
        time = float(lines[-1].split(" ")[3])
    elif(lines[-2].startswith("% time elapsed:")):
        time = float(lines[-2].split(" ")[3])
    elif(lines[-3].startswith("% time elapsed:")):
         time = float(lines[-3].split(" ")[3])
    return lines,time


def run_model(model_file = "View2.mzn", data_file = "Example1.dzn", solver = "Chuffed", VERBOSE = False):

    command = f'minizinc --output_sat-time --solver {solver} --time-limit 60000 "{model_file}" {data_file}'
    return run_command(command, VERBOSE)


def run_model_sat_node_task(data_file = "/sat/SP_Instance_1-sat.txt", type = "node", solver = "g3", VERBOSE = False):

    command = f'python sat_directed_edges-idpool.py {data_file} {type} {solver}'
    return run_command(command, VERBOSE)


def write_output_to_file(filename,output):

    with open(filename, 'w') as f:
        f.write(output)

def main(technology):
    output_folder = "output_sat\\"
    if technology == 'cp':
        path = "data/FRCSP_Instance_*.dzn"
        models = glob.glob("*.mzn")
        #solvers = ["Gecode","Chuffed","HiGHS", "Coin-BC"]
        solvers = ["Gecode"]
        #start creating the csv
        first_row = ["Instance"] + [s for s in solvers for i in range(1,len(models) + 1)]
        second_row = [""] + [m.replace(".mzn","") for i in range(1,len(solvers) + 1) for m in models]
        result_csv = [first_row,second_row]
    else:
        path = "sat/SP_Instance_*-sat.txt"
        # models = ["node", "ordered_task", "unordered_task"]
        models = ["node", "unordered_task"]
        # solvers = ["Gecode","Chuffed","HiGHS", "Coin-BC"]
        solvers = ["g3", "m22"]
        # start creating the csv
        first_row = ["Instance"] + [s for s in solvers]
        second_row = [""] # + [m.replace(".mzn", "") for i in range(1, len(solvers) + 1) for m in models]
        result_csv = [first_row, second_row]

    #write first two rows
    result_csv_file = 'output-five-minutes.csv'
    with open(result_csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(first_row)
        writer.writerow(second_row)
    for data_file in glob.glob(path):
        print(data_file)
        if technology == 'cp':
            row = [data_file.replace("data_bs\\","").replace(".dzn","")]
        else:
            row = [data_file.replace("sat\\", "").replace(".txt", "")]
        for solver in solvers:
            for model in models:
                print(f"Running {model} on {data_file} with {solver}")
                total_output = ""
                total_time = []
                for run in np.arange(1,3):
                    print(f"Run #{run}")
                    if technology == 'cp':
                        output,time = run_model(model_file = model, data_file = data_file,solver = solver, VERBOSE=True)
                    else:
                        output,time = run_model_sat_node_task(data_file = data_file, solver = solver, VERBOSE=True)
                    total_output += output
                    total_time.append(time)
                    if time == None:
                        break
                if total_time[0] == None:
                    average_time = None
                else:
                    average_time = np.mean(total_time)
                row.append(str(average_time).replace("None","t\o"))
                total_output += "Average time: " + str(average_time)
                if technology == 'cp':
                    output_file = output_folder + solver + "\\" + model.replace(".mzn","") + data_file.replace("data\\","").replace(".dzn",".") + ".txt"
                else:
                    output_file = output_folder + solver + "\\" + model + "\\" + data_file.replace("sat\\","")
                #write intermediate output_sat for debud purposes results for debug
                write_output_to_file(output_file,total_output)
        result_csv.append(row)
        with open(result_csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)

    write_output_to_file("output_sat.txt",str(result_csv))


if __name__ == "__main__":
    args = sys.argv

    # Check the number of arguments provided
    num_args = len(args)
    if num_args > 2:
        print("Too many arguments!")
    elif num_args <= 1:
        print("Provide the solving technology that you want to run")
    else:
        technology = args[1]
        if (technology == 'cp') | (technology == 'sat-node-task'):
            main(technology)
        else:
            print("Solving technology can be either cp or sat-node-task!")
