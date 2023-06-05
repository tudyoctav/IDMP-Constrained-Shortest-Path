#ifndef __MIP_SOLVER_H__
#define __MIP_SOLVER_H__

#include <ilcplex/ilocplex.h>
#include "problems.h"
#include <memory>


template<typename> struct Instance;
template<typename> struct Solution;

template<typename ProbT>
class MIPFormulation
{
public:
	virtual void createDecisionVariables(IloEnv env, const Instance<ProbT>& inst) = 0;
	virtual void addConstraints(IloEnv env, IloModel model, const Instance<ProbT>& inst) = 0;
	virtual void addObjectiveFunction(IloEnv env, IloModel model, const Instance<ProbT>& inst) = 0;
	virtual void addUserCallbacks(IloEnv env, IloModel model, IloCplex cplex, const Instance<ProbT>& inst) { }
	virtual void extractSolution(IloCplex cplex, const Instance<ProbT>& inst, Solution<ProbT>& sol) = 0;
};


template<typename ProbT>
class NullFormulation : public MIPFormulation<ProbT>
{
public:
	virtual void createDecisionVariables(IloEnv env, const Instance<ProbT>& inst) { }
	virtual void addConstraints(IloEnv env, IloModel model, const Instance<ProbT>& inst) { }
	virtual void addObjectiveFunction(IloEnv env, IloModel model, const Instance<ProbT>& inst) { }
	virtual void addUserCallbacks(IloEnv env, IloModel model, IloCplex cplex, const Instance<ProbT>& inst) { }
	virtual void extractSolution(IloCplex cplex, const Instance<ProbT>& inst, Solution<ProbT>& sol) { }
};


/**
 * Generic MIP Solver.
 * Subclass from MIPFormulation to write a MIP formulation for a specific problem.
 * See bpformulation.h for an example.
 */
template<typename ProbT>
class MIPSolver
{
public:
	enum Status
	{
		Optimal,     // Returned solution is proven optimal
		Feasible,    // Returned solution is feasible
		Infeasible,  // Instance is infeasible
		Aborted      // There is no feasible solution due to time limits or memory limits
	};

	MIPSolver();
	~MIPSolver();

	template<typename T, typename... Args>
	void setFormulation(Args... args)
	{
		formulation = std::make_unique<T>(std::forward<Args>(args)...);
	}

	template<typename T>
	T* getFormulation() const { return dynamic_cast<T*>(formulation.get()); }

	void setTimeLimit(int time) { m_time_limit = time; }
	void setThreads(int number) { m_threads = number;  }

	Status run(const Instance<ProbT>& inst, Solution<ProbT>& sol);

	int BaBNodes() const { return m_bab_nodes; }  // get number of branch-&-bound nodes from last solve(...) call

protected:
	void initCplex();

private:
	IloEnv env;
	IloModel model;
	IloCplex cplex;

	std::unique_ptr<MIPFormulation<ProbT> > formulation;
	int m_time_limit;  // in seconds -> 0: no time limit
	int m_threads;     // number of used threads, 0: default cplex setting

	int m_bab_nodes;
};

#endif // __MIP_SOLVER_H__

