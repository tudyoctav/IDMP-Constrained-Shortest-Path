#include "rcspformulation.h"

#include "instance.h"
#include "solution.h"
#include "users.h"

#include <utility>


void RCSPFormulation::createDecisionVariables(IloEnv env, const Instance<RCSP>& inst)
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
	int upper = inst.R[inst.t].second;
	y = IloNumVarArray(env, inst.n, 0, upper, ILOINT);
	MIP_OUT(TRACE) << "created " << inst.n << " y_{i} variables" << std::endl;
}

void RCSPFormulation::addConstraints(IloEnv env, IloModel model, const Instance<RCSP>& inst)
{
	std::vector<std::vector<int> > outgoing(inst.n, std::vector<int>());
	std::vector<std::vector<int> > incoming(inst.n, std::vector<int>());
	for (std::pair<int, int> a : inst.A) {
		outgoing[a.first].push_back(a.second);
		incoming[a.second].push_back(a.first);
	}

	// each active node must have exactly one incoming and one outgoing arc
	for (int i : inst.V) if (i != inst.s && i != inst.t) {
		IloExpr sum_in(env); IloExpr sum_out(env); // represents a linear expression of decision variables and constants
		for (int j : incoming[i]) sum_in += x[j][i]; // cplex overloads +,-,... operators
		for (int j : outgoing[i]) sum_out += x[i][j];
		model.add(sum_out - sum_in == 0); // add constraint to model
		sum_in.end(); sum_out.end(); // IloExpr must always call end() to free memory!
	}

	// the source node must have exactly one outgoing arc
	IloExpr sum_s(env);
	for (int j : outgoing[inst.s])
		sum_s += x[inst.s][j];
	model.add(sum_s == 1); sum_s.end();

	// the target node must have exactly one incoming arc
	IloExpr sum_t(env);
	for (int i : incoming[inst.t])
		sum_t += x[i][inst.t];
	model.add(sum_t == 1); sum_t.end();

	MIP_OUT(TRACE) << "added " << inst.n << " constraints to enforce the flow over each node" << std::endl;

	// the arrival time in each node must be within the bounds
	for (int i : inst.V) {
		model.add(y[i] >= inst.R[i].first);
		model.add(y[i] <= inst.R[i].second);
	}

	// the arrival time must be greater than the arrival time of an active edge
	for (int i : inst.V) for (int j : outgoing[i])
		model.add(y[j] >= y[i] + x[i][j] * inst.d[i][j]);
}

void RCSPFormulation::addObjectiveFunction(IloEnv env, IloModel model, const Instance<RCSP>& inst)
{
	IloExpr sum(env);
	for (std::pair<int, int> a : inst.A) {
		int i = a.first; int j = a.second;
		sum += x[i][j] * inst.c[i][j];
	}
	model.add(IloMinimize(env, sum));
	sum.end();
}

void RCSPFormulation::extractSolution(IloCplex cplex, const Instance<RCSP>& inst, Solution<RCSP>& sol)
{
	std::vector<std::vector<int> > outgoing(inst.n, std::vector<int>());
	for (std::pair<int, int> a : inst.A) outgoing[a.first].push_back(a.second);

	// cplex.getValue(x) returns the assigned value of decision variable x
	sol.shortest_path = std::vector<int>();
	sol.arrival_times = std::vector<int>();
	sol.total_cost = 0;
	int node = inst.s;
	while (node != inst.t) {
		for (int j : outgoing[node])
			if (cplex.getValue(x[node][j]) > 0.5) {
				sol.shortest_path.push_back(node);
				sol.arrival_times.push_back(cplex.getValue(y[node]));
				sol.total_cost += inst.c[node][j];
				node = j; break;
			}
	}
	sol.shortest_path.push_back(inst.t);
	sol.arrival_times.push_back(cplex.getValue(y[inst.t]));
}

