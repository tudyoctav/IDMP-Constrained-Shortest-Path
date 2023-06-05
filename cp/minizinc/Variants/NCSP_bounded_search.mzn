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

array[1..nodes] of 0..1: must;

var int: k;


solve :: bool_search(x, dom_w_deg, indomain_min)
           minimize k;


constraint bounded_dpath(nodes, edges, starts, ends, weights, start, end, y, x, k);


% additional constraint: must visit certain nodes
constraint forall(i in 1..nodes) (must[i]=0 \/ y[i]=1);


output
[
  "x: " ++ show(x) ++ "\n" ++
  "y: " ++ show(y) ++ "\n" ++
  "z: " ++ show(k) ++ "\n"
];
