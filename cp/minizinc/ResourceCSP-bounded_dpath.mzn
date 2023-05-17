%------------------------------------------------------------------------------%
% Resource Constrained Shortest Path
% - find the shortest path between the Start node and the End node
% - such that the total travel time is smaller or equal than Time
% - this model used the bounded_dpath global constraint
% model adapted from Jakob Puchinger <jakobp@cs.mu.oz.au> Shortest Path Problem.
%------------------------------------------------------------------------------%
include "globals.mzn";
% Number of nodes
int: N;
% Start node
1..N: Start;
% End node
1..N: End;
% Max arrival Time
int: Time;
% Number of edges (directed arcs)
int: M;
% Edge lengths
array[1..M] of int: L;
% Edge travel time
array[1..M] of int: T;

% 1..N upper and lower resource bounds
array[1..N] of int: Lower_Bound;
array[1..N] of int: Upper_Bound;

% Edge start node
array[1..M] of 1..N: Edge_Start;
array[1..M] of 1..N: Edge_End;

% Variable indicating if edge is used
array[1..M] of var bool: x;
% Variable indicating if vertex u is used (need it for dpath)
array[1..N] of var bool: y;
% total cost and time of the path

var int: total_length;
var int: total_time;
constraint bounded_dpath(N, M, Edge_Start, Edge_End, L , Start, End, y, x, total_length);
constraint bounded_dpath(N, M, Edge_Start, Edge_End, T , Start, End, y, x, total_time);

constraint (total_time <= Time);
solve minimize total_length;

output ["Length: ", show(sum(e in 1..M)(L[e] * x[e])), "\n"] ++
       ["Start : ", show(Start), "\n"] ++
       ["End   : ", show(End), "\n\n"] ++
       ["1..M in shortest path:\n"] ++
       [ if   fix(x[e]) = 1
         then show(Edge_Start[e]) ++ " -> " ++ show(Edge_End[e]) ++ "\n" 
         else "" 
         endif | e in 1..M
       ]
%        ++
%        [ 
%          show(y[i]) | i in 1..N
%        ]
       ;
%------------------------------------------------------------------------------%
%------------------------------------------------------------------------------%