import subprocess
from tqdm import tqdm
from itertools import takewhile

ms = [1, 2, 3, 4, 5]
ns = [10, 15, 20, 25, 30, 35, 40, 45, 50, 100]
ninst = 10  # total = 500 instances

t = 900
prob = "NCSP"  # NCSP (Node Constrained) - TCSP (Task Constrained) - RCSP (Resource Constrained)
result = ""
infeasible = 0

for m in tqdm(ms, desc="m"):
    for n in tqdm(ns, desc="n"):
        avg_v = 0
        avg_t = 0
        for i in tqdm(range(ninst), desc="inst"):
            inst = "m{:02d}_n{:04d}__{:03d}".format(m, n, i)
            input_str = "..\\x64\\Debug\\MIP-RCSP.exe ifile ..\\inst\\{}.inst prob {} ttime {}".format(inst, prob, t)

            try:
                res = subprocess.run(input_str, shell=True, capture_output=True, text=True)
                output = res.stdout
                err = res.stderr

                a1 = output[output.index('best objective value:') + len('best objective value:'):]
                value = a1[:a1.index('\n')].strip()
                avg_v += float(value)

                a2 = output[output.index('CPU time:') + len('CPU time:'):]
                time = a2[:a2.index('\n')].strip()
                avg_t += float(time)

                a3 = output[output.index('CPLEX status:') + len('CPLEX status:'):]
                b = a3[:a3.index('\n')].strip()
                status = ''.join(takewhile(lambda x: str.isalpha(x), b))

                if status != "Optimal":
                    result += "error: {} -> Status: {} -> Value: {} -> Time: {}".format(inst, status, value, time) + '\n'
                    print(" encountered status: " + status + " on inst: " + inst)

                if err:
                    print(" encountered error: " + err + " in inst: " + inst)
                    infeasible += 1

            except subprocess.TimeoutExpired:
                break

        result += "m{:02d}_n{:04d}".format(m, n) + \
                  " -> Value: " + str(avg_v / ninst) + \
                  " -> Time: " + str(round(avg_t / ninst, 4)) + '\n'

if infeasible > 0:
    result += str(infeasible) + " infeasible solutions"
print(result)

file = open("test_{}.txt".format(prob), "w")
file.write(result)
file.close()
