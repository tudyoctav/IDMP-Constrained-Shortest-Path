#include "tcspformulation.h"

#include "instance.h"
#include "solution.h"
#include "users.h"

#include <utility>


void TCSPFormulation::createDecisionVariables(IloEnv env, const Instance<TCSP>& inst)
{
	// decision variables x_{ij}
	x = IloArray<IloNumVarArray>(env, inst.n);  // create array of decision variables (inst.n elements)
	for (int i : inst.V)
		x[i] = IloNumVarArray(env, inst.n, 0, 1, ILOBOOL);
	//                               ^     ^  ^     ^
	//                               |     |  |     +------ variable type: ILOINT for integers
	//                               |     |  +------------ maximum value of variables
	//                               |     +--------------- minium value of variables
	//                               +--------------------- number of variables
	MIP_OUT(TRACE) << "created " << inst.n * inst.n << " x_{ij} variables" << std::endl;

	// decision variables y_j
	y = IloNumVarArray(env, inst.n, 0, 1, ILOBOOL);
	MIP_OUT(TRACE) << "created " << inst.n << " y_{i} variables" << std::endl;
}

void TCSPFormulation::addConstraints(IloEnv env, IloModel model, const Instance<TCSP>& inst)
{
	std::vector<std::vector<int> > outgoing(inst.n, std::vector<int>());
	std::vector<std::vector<int> > incoming(inst.n, std::vector<int>());
	for (std::pair<int, int> a : inst.A) {
		outgoing[a.first].push_back(a.second);
		incoming[a.second].push_back(a.first);
	}

	// the flow that enters a node must also leave the node
	for (int i : inst.V) {
		IloExpr sum_in(env); IloExpr sum_out(env); // represents a linear expression of decision variables and constants
		for (int j : incoming[i]) sum_in += x[j][i]; // cplex overloads +,-,... operators
		for (int j : outgoing[i]) sum_out += x[i][j]; 
		model.add(sum_in <= 1); model.add(sum_out <= 1); // add constraint to model

		int sum = (i == inst.s) - (i == inst.t);
		model.add(sum_out - sum_in == sum);
		model.add(y[i] <= sum_in + sum_out); // node can only be active if there's flow
		sum_in.end(); sum_out.end(); // IloExpr must always call end() to free memory!
	}
	
	/** the source node must send out one unit of flow
	IloExpr sum_s(env);
	for (int j : outgoing[inst.s])
		sum_s += x[inst.s][j];
	model.add(sum_s == 1); sum_s.end();

	// the target node must receive one unit of flow
	IloExpr sum_t(env);
	for (int i : incoming[inst.t])
		sum_t += x[i][inst.t];
	model.add(sum_t == 1); sum_t.end(); //*/
	
	MIP_OUT(TRACE) << "added " << inst.n << " constraints to enforce the flow over each node" << std::endl;

	// for each required task, there should be an active node containing that task
	for (std::vector<int> t : inst.T) {
		IloExpr sum(env);
		for (int i : t) sum += y[i];
		model.add(sum >= 1); sum.end();
	}

}

void TCSPFormulation::addObjectiveFunction(IloEnv env, IloModel model, const Instance<TCSP>& inst)
{
	IloExpr sum(env);
	for (std::pair<int, int> a : inst.A) {
	  int i = a.first; int j = a.second;
	  sum += x[i][j] * inst.c[i][j];
	}
	model.add(IloMinimize(env, sum));
	sum.end();
}

void TCSPFormulation::extractSolution(IloCplex cplex, const Instance<TCSP>& inst, Solution<TCSP>& sol)
{
	std::vector<std::vector<int> > outgoing(inst.n, std::vector<int>());
	for (std::pair<int, int> a : inst.A) outgoing[a.first].push_back(a.second);

	// cplex.getValue(x) returns the assigned value of decision variable x
	sol.shortest_path = std::vector<int>();
	sol.total_cost = 0;
	int node = inst.s;
	while (node != inst.t) {
		for (int j : outgoing[node])
			if (cplex.getValue(x[node][j]) > 0.5) {
				sol.shortest_path.push_back(node);
				sol.total_cost += inst.c[node][j];
				node = j; break;
			}
	}
	sol.shortest_path.push_back(inst.t);
}

