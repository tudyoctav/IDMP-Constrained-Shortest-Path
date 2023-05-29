# IDMP-Constrained-Shortest-Path
 This project explores CP, SAT, and MIP technologies for solving the Constrained Shortest Path problem and compares their performance.

### Instalation
```bash
pip install -r requirements.txt
```

### Running Resource Constrained Shortest Path (RCSP):
Where you should replace `../cp/minizinc` with the path to the folder containing the test instances
```bash
python ./run_all resource_constraint ../cp/minizinc
```

### Running Time Windowed Shortest Path (TWSP)
Where you should replace `../cp/minizinc` with the path to the folder containing the test instances
```bash
python ./run_all time_window ../cp/minizinc
```

### Additional options
Additional options can be set by supplying them from the command line.
The options available are:
```bash
options:
  -h, --help            show this help message and exit
  -t TIME_OUT, --time-out TIME_OUT
                        The timeout after which to terminate the solver in seconds
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        The file to write the timing information to.
  -s SOLVERS [SOLVERS ...], --solvers SOLVERS [SOLVERS ...]
                        The name of the solvers to use, more than one value can be specified.
  -r REPEATS, --repeats REPEATS
                        The number of times to repeat the solver to get an average
  --std_out_dir STD_OUT_DIR
                        Path to folder where to store the outputs of the solvers.
```
You can also call the run_all script from python by importing the run_all function
```python
run_all("time_window", "../cp/minizinc", time_out=5)
```

### Running a single file
Running a single file uses similair syntax as before. However The results are not stored in a file!
```bash
python ./model {resource_constraint,time_window} instance_folder
```