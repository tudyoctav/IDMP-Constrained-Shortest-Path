#ifndef __RCSP_FORMULATION_H__
#define __RCSP_FORMULATION_H__

#include "problems.h"
#include "mipsolver.h"

template<typename> struct Instance;
template<typename> struct Solution;

/**
 * MIP Formulation for the Resource Constrained Shortest Path.
 * Uses two kinds of binary decision variables:
 *
 *  *) x_{ij} -> arc (i, j) is active
 *  *) y_j    -> node j is active
 *
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

	// binary decision variables y_j: node j is used (=1) or not (=0)
	IloNumVarArray y;
};


#endif // __RCSP_FORMULATION_H__
