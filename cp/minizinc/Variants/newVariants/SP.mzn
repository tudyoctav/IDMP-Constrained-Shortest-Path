%------------------------------------------------------------------------------%
% Full Resource Constrained Shortest Path
% - find the shortest path between the Start node and the End node
% - such that our leaving time (left[i]) at each node is 
%   greater or equal with the lower bound of that node and
%   smaller or equal with the upper bound of that node
% model adapted from Jakob Puchinger <jakobp@cs.mu.oz.au> Shortest Path Problem.
%------------------------------------------------------------------------------%

% Number of nodes
int: N;
% Start node
1..N: Start;
% End node
1..N: End;
% Number of edges (directed arcs)
int: M;
% Edge lengths
array[1..M] of int: L;

% Edge start node
array[1..M] of 1..N: Edge_Start;
array[1..M] of 1..N: Edge_End;

% Variable indicating if edge is used
array[1..M] of var 0..1: x;

constraint
    forall( i in 1..N ) (
        if i = Start then
                % outgoing flow
            sum(e in 1..M where Edge_Start[e] = i)(x[e]) - 
                % incoming flow
            sum(e in 1..M where Edge_End[e] = i)(x[e])
            = 1
        elseif i = End then
            sum(e in 1..M where Edge_Start[e] = i)(x[e]) - 
            sum(e in 1..M where Edge_End[e] = i)(x[e])
            = -1
        else
            sum(e in 1..M where Edge_Start[e] = i)(x[e]) - 
            sum(e in 1..M where Edge_End[e] = i)(x[e])
            = 0
        endif
    );

solve minimize sum(e in 1..M)( L[e] * x[e] );

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
%          "Node " ++ show(i) ++ " left at time " ++ show(left[i]) ++ " (took: " ++ show(time[i]) ++ " to arrive at this node)\n" 
%          | i in 1..N
%        ]
       ;
