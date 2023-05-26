#ifndef __RCSP_FORMULATION_H__
#define __RCSP_FORMULATION_H__

#include "problems.h"
#include "mipsolver.h"

template<typename> struct Instance;
template<typename> struct Solution;

/**
 * MIP Formulation for the Resource Constrained Shortest Path.
 * Uses two kinds of decision variables:
 *
 *  *) x_{ij} -> arc (i, j) is active
 *  *) y_j    -> arrival time at node j
 * 
 * The arrival time of any node is upperbounded by
 * the maximum arrival time of the target node.
 */
class RCSPFormulation : public MIPFormulation<RCSP>
{
public:
	// create all required decision variables
	virtual void createDecisionVariables(IloEnv env, const Instance<RCSP>& inst) override;

	// add all constraints to the model
	virtual void addConstraints(IloEnv env, IloModel model, const Instance<RCSP>& inst) override;

	// add objective function to the model
	virtual void addObjectiveFunction(IloEnv env, IloModel model, const Instance<RCSP>& inst) override;

	// derive solution from the cplex object
	virtual void extractSolution(IloCplex cplex, const Instance<RCSP>& inst, Solution<RCSP>& sol) override;

private:
	// binary decision variables x_{ij}: the arc from i to j is active (=1) or not (=0)
	IloArray<IloNumVarArray> x;

	// integer decision variables y_j: node j is reached at time y_j
	IloNumVarArray y;
};


#endif // __RCSP_FORMULATION_H__
