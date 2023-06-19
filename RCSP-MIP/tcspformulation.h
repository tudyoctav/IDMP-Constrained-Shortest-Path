#ifndef __TCSP_FORMULATION_H__
#define __TCSP_FORMULATION_H__

#include "problems.h"
#include "mipsolver.h"

template<typename> struct Instance;
template<typename> struct Solution;

/**
 * MIP Formulation for the Node Constrained Shortest Path.
 * Uses two kinds of binary decision variables:
 *
 *  *) x_{ij} -> arc (i, j) is active
 *  *) y_j    -> node j is active
 *
 */
class TCSPFormulation : public MIPFormulation<TCSP>
{
public:
	// create all required decision variables
	virtual void createDecisionVariables(IloEnv env, const Instance<TCSP>& inst) override;

	// add all constraints to the model
	virtual void addConstraints(IloEnv env, IloModel model, const Instance<TCSP>& inst) override;

	// add objective function to the model
	virtual void addObjectiveFunction(IloEnv env, IloModel model, const Instance<TCSP>& inst) override;

	// derive solution from the cplex object
	virtual void extractSolution(IloCplex cplex, const Instance<TCSP>& inst, Solution<TCSP>& sol) override;

private:
	// binary decision variables x_{ij}: the arc from i to j is active (=1) or not (=0)
	IloArray<IloNumVarArray> x;

	// binary decision variables y_j: node j is used (=1) or not (=0)
	IloNumVarArray y;
};


#endif // __TCSP_FORMULATION_H__
