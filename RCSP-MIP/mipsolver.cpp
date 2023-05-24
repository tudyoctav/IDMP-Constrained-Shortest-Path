#include "mipsolver.h"


#include "solution.h"
#include "instance.h"
#include "users.h"

#include "lib/util.h"

#include <stdexcept>
#include <algorithm>

ILOSTLBEGIN

template<typename ProbT>
MIPSolver<ProbT>::MIPSolver() : m_time_limit(0), m_threads(0), m_bab_nodes(0)
{
	formulation = make_unique<NullFormulation<ProbT> >();
}

template<typename ProbT>
MIPSolver<ProbT>::~MIPSolver()
{
	cplex.end();
	model.end();
	env.end();
}

template<typename ProbT>
typename MIPSolver<ProbT>::Status MIPSolver<ProbT>::run(const Instance<ProbT>& inst, Solution<ProbT>& sol)
{
	initCplex();
	MIP_OUT(DBG) << "init CPLEX" << std::endl;

	try {
		formulation->createDecisionVariables(env, inst);
		MIP_OUT(DBG) << "created decision variables" << std::endl;

		formulation->addConstraints(env, model, inst);
		MIP_OUT(DBG) << "created constraints" << std::endl;

		formulation->addObjectiveFunction(env, model, inst);
		MIP_OUT(DBG) << "created objective function" << std::endl;

		cplex = IloCplex(model);
		MIP_OUT(DBG) << "initated cplex model" << std::endl;
		if (m_threads != 0)
			cplex.setParam(IloCplex::Param::Threads, m_threads);
		if (m_time_limit != 0)
			cplex.setParam(IloCplex::Param::TimeLimit, m_time_limit);

		formulation->addUserCallbacks(env, model, cplex, inst);

#ifndef USER_MIP
		cplex.setOut(env.getNullStream());
		cplex.setWarning(env.getNullStream());
		cplex.setError(env.getNullStream());
#endif

//		cplex.setParam(IloCplex::Param::MIP::Limits::Nodes, 1); // Stop after root node.

		MIP_OUT(DBG) << "calling CPLEX solve ..." << std::endl;
		cplex.solve();
		MIP_OUT(DBG) << "CPLEX finished." << std::endl;
		IloAlgorithm::Status stat = cplex.getStatus();
		m_bab_nodes = (int)cplex.getNnodes();
		MIP_OUT(DBG) << "CPLEX status: " << stat << std::endl;
		if (stat == IloAlgorithm::Optimal || stat == IloAlgorithm::Feasible) {
			formulation->extractSolution(cplex, inst, sol);
			MIP_OUT(TRACE) << "Solution: \n" << sol << std::endl;
			MIP_OUT(DBG) << "Objective value: " << cplex.getObjValue() << std::endl;
			MIP_OUT(DBG) << "Lower Bound: " << cplex.getBestObjValue() << std::endl;
			MIP_OUT(DBG) << "Branch-and-Bound nodes: " << m_bab_nodes << std::endl;
			if (stat == IloAlgorithm::Optimal) {
				sol.db = (int)cplex.getObjValue();
				return Optimal;
			} else {
				sol.db = (int)cplex.getBestObjValue();
				return Feasible;
			}
		} else if (stat == IloAlgorithm::Infeasible) {
			throw std::runtime_error("Intance is infeasible");
		} else {
			MIP_OUT(FATAL) << "No feasible solution exists" << std::endl;
			return Aborted;
		}

	} catch(IloException& e) {
		throw std::runtime_error(e.getMessage());
	} catch(...) {
		throw std::runtime_error("Unknown exception");
	}
}

template<typename ProbT>
void MIPSolver<ProbT>::initCplex()
{
	try {
		env = IloEnv();
		model = IloModel(env);
	} catch(IloException& e) {
		throw std::runtime_error(e.getMessage());
	} catch(...) {
		throw std::runtime_error("Unknown exception");
	}
}

// Instantiate all required MIP solver classes
template class MIPSolver<SP>;
template class MIPSolver<RCSP>;

