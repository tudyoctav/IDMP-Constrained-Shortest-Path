include "globals.mzn";

int: nodes;
int: edges;
int: start;
int: end;

int: tasks;

array[1..edges] of int: starts;
array[1..edges] of int: ends;
array[1..edges] of int: weights;

array[1..edges] of var bool: x;
array[1..nodes] of var bool: y;

array[1..tasks,1..nodes] of 0..1: task;

var int: k;


solve :: bool_search(x, dom_w_deg, indomain_min)
        :: restart_linear(1000)
           minimize k;


constraint bounded_dpath(nodes, edges, starts, ends, weights, start, end, y, x, k);


% task-constrained
constraint forall(t in 1..tasks) ((sum(i in 1..nodes) (task[t,i]*y[i])) > 0);
