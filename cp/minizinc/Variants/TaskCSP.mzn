include "globals.mzn";

int: nodes;
int: edges;
int: start;
int: end;

int: tasks;

% array[1..edges,1..3] of int: edge;
array[1..edges] of int: starts;
array[1..edges] of int: ends;
array[1..edges] of int: weights;

array[1..edges] of var bool: x;
array[1..nodes] of var bool: y;

array[1..nodes] of var 0..1: must;

array[1..tasks,1..nodes] of 0..1: task;


% var int: z = sum(i in 1..edges) (edge[i,3]*x[i]);
var int: z = sum(i in 1..edges) (weights[i]*x[i]);
solve minimize z;


% constraint dpath(nodes, edges, [edge[i, 1] | i in 1..edges], [edge[i, 2] | i in 1..edges], start, end, y, x);
constraint dpath(nodes, edges, starts, ends, start, end, y, x);


% task-constrained
constraint forall(t in 1..tasks) ((sum(i in 1..nodes) (task[t,i]*y[i])) > 0);
% constraint forall(t in 1..tasks) (exists(i in 1..nodes) (task[t,i]*y[i] > 0));


output
[
  "x: " ++ show(x) ++ "\n" ++
  "y: " ++ show(y) ++ "\n" ++
  "z: " ++ show(z) ++ "\n"
];

