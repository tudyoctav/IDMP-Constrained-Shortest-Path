%------------------------------------------------------------------------------%
% Full Resource Constrained Shortest Path
% - find the shortest path between the Start node and the End node
% - such that our leaving time (left[i]) at each node is 
%   greater or equal with the lower bound of that node and
%   smaller or equal with the upper bound of that node
% - this model used the dpath global constraint
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

%Leaving time for each vertex
array[1..N] of var int: left;

% Previous and next node for each selected vertex
% array[1..N] of var 0..N: next;
array[1..N] of var int: time;
array[1..N] of var 0..N: prev;

constraint dpath(Edge_Start, Edge_End, Start, End, y, x);

% construcst the prev array (for simplicity)
constraint
    prev[Start] = 0 /\ time[Start] = 0 /\
    %for each edge in the path
    forall( i in 1..M where x[i] == 1) (
      % enforce previous node and the time to travel the edge between them
      prev[Edge_End[i]] =  Edge_Start[i] /\ time[Edge_End[i]] = T[i]
    );  

% enforces the resource constraint 
constraint
    forall(i in 1..N ) (
        if i = Start then
             % we can not leave before lower bound or after the upper bound
             Lower_Bound[i] <= left[i] /\ left[i] <= Upper_Bound[i]
        else
             Lower_Bound[i] <= left[i] /\ left[i] <= Upper_Bound[i] /\
             % we can not leave before we arrive 
             %(leaving time must be greater than leaving time of previous node + time it took to arrive here)
              (left[i] >= left[prev[i]] + time[i])
        endif
    );
      
solve :: bool_search(x, dom_w_deg, indomain_min)
      :: restart_linear(1000)
      minimize sum(e in 1..M)( L[e] * x[e] );

output ["Length: ", show(sum(e in 1..M)(L[e] * x[e])), "\n"] ++
       ["Start : ", show(Start), "\n"] ++
       ["End   : ", show(End), "\n\n"] ++
       ["1..M in shortest path:\n"] ++
       [ if   fix(x[e]) = 1
         then "Edge " ++ show(e) ++ " : " ++ show(Edge_Start[e]) ++ " -> " ++ show(Edge_End[e]) ++ "\n" 
         else "" 
         endif | e in 1..M
       ] 
%        ++
%        [
%          if   fix(y[i]) = 1
%          then "Node " ++ show(i) ++ " left at time " ++ show(left[i]) ++ " (took: " ++ show(time[i]) ++ " to arrive at this node)\n"  
%          else "" 
%          endif | i in 1..N
%        ]
       ;
