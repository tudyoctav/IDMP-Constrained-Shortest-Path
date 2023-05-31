#include <iostream>
#include <fstream>
#include <stdexcept>
#include <algorithm>

#include "lib/util.h"
#include "lib/log.h"
#include "lib/lutze.h"      // time measurement
#include "lib/argparser.h"  // simple command line argument parser

#include "users.h"              // register users/submodules for writing to stdout, register your own user name for writing to stdout
#include "problems.h"           // contains for each problem a struct type that is used in other classes / algorithms
#include "instance.h"           // contains for each problem an instance class that contains all information related to a specific instance of a problem
#include "solution.h"           // contains for each problem a solution class that represents a solution to a specific instance

// MIP stuff
#include "mipsolver.h"          // generic mip solver, uses CPLEX to solve mips
#include "ncspformulation.h"
#include "tcspformulation.h"
#include "rcspformulation.h"

int main(int argc, char* argv[])
{
  int ticket = LuTze::start();  // get ticket for time measurement

  //SOUT() << "# version: " << VERSION << std::endl;  // print git version to stdout

  // read command line arguments
  ArgParser arg_parser(argc, argv);

  try {
	arg_parser.add<std::string>("ifile", "Input file", "inst/bp/bp1.inst");
	arg_parser.add<std::string>("prob", "Problem: Node Constrained Shortest Path (NCSP), Resource Constrained Shortest Path (RCSP)", "NCSP", { "NCSP", "RCSP" });
	arg_parser.add<int>("ttime", "total time limit", 0, 0, std::numeric_limits<int>::max());
	arg_parser.add<int>("threads", "Number of used threads", 1, 0, 100);

	if (arg_parser.isHelpSet()) {
	  arg_parser.help(std::cout);
	  return EXIT_SUCCESS;
	}

	arg_parser.parse();
  }
  catch (const std::exception& exp) {
	std::cerr << "ERROR: " << exp.what() << std::endl;
	return EXIT_FAILURE;
  }

  SOUT() << arg_parser;  // print arguments to stdout

  std::string instance_filename = arg_parser.get<std::string>("ifile");

  if (arg_parser.get<std::string>("prob") == "NCSP") {
	/*****************************************************************************************/
	/** Node Constrained Shortest Path *******************************************************/
	/*****************************************************************************************/
	Instance<NCSP> inst(instance_filename);  // read NCSP instance

	SOUT() << "instance: " << instance_filename << std::endl;
	SOUT() << "\t" << inst << std::endl;

	Solution<NCSP> sol(inst);  // create empty NCSP solution

	// setup MIP solver
	MIPSolver<NCSP> mip_solver;
	mip_solver.setTimeLimit(arg_parser.get<int>("ttime"));  // set time limit; 0 -> no time limit
	mip_solver.setThreads(arg_parser.get<int>("threads"));  // number of used threads, should be always one for our experiments

	mip_solver.setFormulation<NCSPFormulation>();  // set MIP formulation

	/**************************************************************/
	auto status = mip_solver.run(inst, sol);  /** run MIP solver **/
	/**************************************************************/

	if (status == MIPSolver<NCSP>::Feasible || status == MIPSolver<NCSP>::Optimal) {
	  SOUT() << std::endl;
	  SOUT() << "# best solution:" << std::endl;
	  SOUT() << "best objective value:\t" << inst.objective(sol) << std::endl;
	  SOUT() << "best dual bound value:\t" << sol.db << std::endl;
	  SOUT() << "optimality gap:\t" << (double)(inst.objective(sol) - sol.db) / (double)inst.objective(sol) * 100.0 << "%" << std::endl;
	  SOUT() << "solution:\t\n" << sol.shortest_path << std::endl;
	}

  }
  else if (arg_parser.get<std::string>("prob") == "TCSP") {
	  /*****************************************************************************************/
	  /** Task Constrained Shortest Path *******************************************************/
	  /*****************************************************************************************/
	  Instance<TCSP> inst(instance_filename);  // read TCSP instance

	  SOUT() << "instance: " << instance_filename << std::endl;
	  SOUT() << "\t" << inst << std::endl;

	  Solution<TCSP> sol(inst);  // create empty TCSP solution

	  // setup MIP solver
	  MIPSolver<TCSP> mip_solver;
	  mip_solver.setTimeLimit(arg_parser.get<int>("ttime"));  // set time limit; 0 -> no time limit
	  mip_solver.setThreads(arg_parser.get<int>("threads"));  // number of used threads, should be always one for our experiments

	  mip_solver.setFormulation<TCSPFormulation>();  // set MIP formulation

	  /**************************************************************/
	  auto status = mip_solver.run(inst, sol);  /** run MIP solver **/
	  /**************************************************************/

	  if (status == MIPSolver<TCSP>::Feasible || status == MIPSolver<TCSP>::Optimal) {
		  SOUT() << std::endl;
		  SOUT() << "# best solution:" << std::endl;
		  SOUT() << "best objective value:\t" << inst.objective(sol) << std::endl;
		  SOUT() << "best dual bound value:\t" << sol.db << std::endl;
		  SOUT() << "optimality gap:\t" << (double)(inst.objective(sol) - sol.db) / (double)inst.objective(sol) * 100.0 << "%" << std::endl;
		  SOUT() << "solution:\t\n" << sol.shortest_path << std::endl;
	  }

  }
  else if (arg_parser.get<std::string>("prob") == "RCSP") {
	/*****************************************************************************************/
	/** Resource Constrained Shortest Path ***************************************************/
	/*****************************************************************************************/
	Instance<RCSP> inst(instance_filename);  // read RCSP instance

	SOUT() << "instance: " << instance_filename << std::endl;
	SOUT() << "\t" << inst << std::endl;

	Solution<RCSP> sol(inst);  // create empty BP solution

	// setup MIP solver
	MIPSolver<RCSP> mip_solver;
	mip_solver.setTimeLimit(arg_parser.get<int>("ttime"));  // set time limit; 0 -> no time limit
	mip_solver.setThreads(arg_parser.get<int>("threads"));  // number of used threads, should be always one for our experiments

	mip_solver.setFormulation<RCSPFormulation>();  // set MIP formulation

	/**************************************************************/
	auto status = mip_solver.run(inst, sol);  /** run MIP solver **/
	/**************************************************************/

	if (status == MIPSolver<RCSP>::Feasible || status == MIPSolver<RCSP>::Optimal) {
		SOUT() << std::endl;
		SOUT() << "# best solution:" << std::endl;
		SOUT() << "best objective value:\t" << inst.objective(sol) << std::endl;
		SOUT() << "best dual bound value:\t" << sol.db << std::endl;
		SOUT() << "optimality gap:\t" << (double)(inst.objective(sol) - sol.db) / (double)inst.objective(sol) * 100.0 << "%" << std::endl;
		SOUT() << "solution:\t\n" << sol.shortest_path << std::endl;
		SOUT() << sol.arrival_times << std::endl;
	}

  }
}
