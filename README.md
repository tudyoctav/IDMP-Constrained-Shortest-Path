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
python sat_directed_edges.py .sat/SP_Instance_1-sat.txt node
```

### For running TCSP: (You need to add the number of task sets at the end of first line ...)
```bash
python sat_directed_edges.py .sat/SP_Instance_1-sat.txt task
```