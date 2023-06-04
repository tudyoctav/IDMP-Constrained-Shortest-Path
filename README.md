# IDMP-Constrained-Shortest-Path
 This project explores CP, SAT, and MIP technologies for solving the Constrained Shortest Path problem and compares their performance.

### Generating graphs
To generate the graph, move to the `graph_generation` run the following commands:
```
cd graph_generation
python generate_demo_graphs.py
```

The graph will be drawn and saved in the `graph_generation/graphs` folder.
![Example graphs](graph_generation/example.png)

To convert the graphs to the format used by the solvers, run the following command:
```
python read_graphs.py
```

The new files will be saved in the `graph_generation/data` folder.

### To convert .dzn instances to txt file use the following:
First, put the .dzn files that you want to convert in a `data` folder together with the `convert.py`.
Next create an empty sat folder and run the following command:

```bash
python convert.py data/FRCSP_Instance_1.dzn
```

## Instructions for solving with CP

Navigate to ```cp/minizinc/Variants```. There you will find the ```run_all.py``` file which takes a single argument determining the type of problem to solve. To solve the Full Resource CSP, use ```frcsp```. To solve the Task-Constrained CSP, use ```tcsp```. The resulting command will look as follows:

```bash
python run_all.py tcsp
```

## Instructions for solving with SAT

### For running NCSP:
Navigate to sat-node-task folder and run:
```bash
python sat_directed_edges-idpool.py data-txt/SP_Instance_1-sat.txt node g3
```

### For running TCSP - ordered or unordered: (You need to add the number of task sets at the end of first line ...)
Navigate to sat-node-task folder and run:
```bash
python sat_directed_edges-idpool.py data-txt/SP_Instance_1-data.txt unordered_task g3
```

### Running with run_all.py for NCSP and TCSP
Navigate to sat-node-task folder and perform the following steps:
First create a folder output_sat, then inside it create a folder for each solver that you are planning to run - cadical153,
(g3 and m22). In each solver folder, create two subfolders - node and unordered_task. 
Finally, to run all instances in data-txt folder as follows:
```bash
python run_all_with_sat.py sat-node-task
```

### Running lab

#### Prerequisits

* Python version >= 3.7
    * For windows systems pysat may fail to install in which case try downgrading python to version <= 3.8 (see: the [Pysat Github](https://github.com/pysathq/pysat/issues/7#issuecomment-784543851))
* Some compiler for MIP???

#### Installation

We recommend installing the requirements in a [Python virtual environment](https://docs.python.org/3/tutorial/venv.html). This has the advantage that there are no modifications to the system-wide configuration.

To setup the virtual environment:

```powershell
python -m venv venv
```

Then to activate the virtual envionment run:

##### Windows

```powershell
venv\Scripts\Scripts\Activate.ps1
```

##### **Linux** and **Mac**:

```bash
source venv/bin/activate
```



To install the requirements run:

```bash
python -m pip install -r requirements.txt
```

#### Running

To run all the steps for the expirments run:

```bash
python run_lab.py --all
```

To see all the steps available run:

```
python run_lab.py
```

To run specific steps you can execute the `run_lab.py` script with the index or name of the steps for example:

```bash
python run_lab.py 1 2 # Will build and run all experiments
```
```bash
python run_lab.py parse-again # Will parse all the experiments
```
```bash
python run_lab.py 5 6 7 8 9 # Will generate all the reports
```

