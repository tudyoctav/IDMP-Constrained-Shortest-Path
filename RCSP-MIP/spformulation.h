#ifndef __SP_FORMULATION_H__
#define __SP_FORMULATION_H__

#include "problems.h"
#include "mipsolver.h"

template<typename> struct Instance;
template<typename> struct Solution;

/**
 * MIP Formulation for the Shortest Path.
 * Uses one kind of binary decision variables:
 *
 *  *) x_{ij} -> arc (i, j) is active
 *
 */
class SPFormulation : public MIPFormulation<SP>
{
public:
	// create all required decision variables
	virtual void createDecisionVariables(IloEnv env, const Instance<SP>& inst) override;

	// add all constraints to the model
	virtual void addConstraints(IloEnv env, IloModel model, const Instance<SP>& inst) override;

	// add objective function to the model
	virtual void addObjectiveFunction(IloEnv env, IloModel model, const Instance<SP>& inst) override;

	// derive solution from the cplex object
	virtual void extractSolution(IloCplex cplex, const Instance<SP>& inst, Solution<SP>& sol) override;

private:
	// binary decision variables x_{ij}: the arc from i to j is active (=1) or not (=0)
	IloArray<IloNumVarArray> x;
};


#endif // __SP_FORMULATION_H__
