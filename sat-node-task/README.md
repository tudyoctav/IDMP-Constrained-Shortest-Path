# IDMP-Constrained-Shortest-Path
 This project explores CP, SAT, and MIP technologies for solving the Constrained Shortest Path problem and compares their performance.

### To convert .dzn instances to txt file use the following:
First, put the .dzn files that you want to convert in a cp_instances folder.
Next create an empty sat folder and run the following command:

```bash
python convert.py data/FRCSP_Instance_1.dzn
```

### For running NCSP:

```bash
python sat_directed_edges-idpool.py data-txt/SP_Instance_1-sat.txt node g3
```

### For running TCSP - ordered or unordered: (You need to add the number of task sets at the end of first line ...)
```bash
python sat_directed_edges-idpool.py data-txt/SP_Instance_1-data.txt unordered_task g3
```

### Running with run_all.py
First create a folder output_sat, then inside it create to folders - g3 and m22. 
In each one of them, create two subfolders - node and unordered_task. 
Finally, to run all instances in the sat folder, run:
```bash
python run_all_with_sat.py sat-node-task
```