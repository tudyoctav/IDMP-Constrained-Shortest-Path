include "globals.mzn";

int: nodes;
int: edges;
int: start;
int: end;

array[1..edges] of int: starts;
array[1..edges] of int: ends;
array[1..edges] of int: weights;

array[1..edges] of var bool: x;
array[1..nodes] of var bool: y;

array[1..nodes] of int: p;


var int: z = sum(i in 1..edges) (weights[i]*x[i]) + sum(i in 1..nodes) ((1-y[i])*p[i]);


solve :: bool_search(x, dom_w_deg, indomain_min)
        :: restart_linear(1000)
           minimize z;


constraint dpath(nodes, edges, starts, ends, start, end, y, x);



output
[
  "x: " ++ show(x) ++ "\n" ++
  "y: " ++ show(y) ++ "\n" ++
  "z: " ++ show(z) ++ "\n"
];
