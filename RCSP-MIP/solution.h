#ifndef __SOLUTION_H__
#define __SOLUTION_H__


#include "problems.h"
#include "instance.h"

#include <vector>
#include <tuple>
#include <algorithm>


/*
 * Generic solution.
 * To write a solution class for a specific problem,
 * specialize this class for the corresponding problem type.
 */
template<typename ProbT>
struct Solution { };




/*****************************************************************************************/
/** Shortest Path Problem ****************************************************************/
/*****************************************************************************************/
template<>
struct Solution<SP>
{
  Solution(const Instance<SP>& inst);
  std::vector<int> shortest_path;
  int total_cost;
  double db;  // dual bound
};

std::ostream& operator<<(std::ostream& os, const Solution<SP>& sol);




/*****************************************************************************************/
/** Resource Constrained Shortest Path ***************************************************/
/*****************************************************************************************/
template<>
struct Solution<RCSP>
{
	Solution(const Instance<RCSP>& inst);
	std::vector<int> shortest_path;
	std::vector<int> arrival_times;
	int total_cost;
	double db;  // dual bound
};

std::ostream& operator<<(std::ostream& os, const Solution<RCSP>& sol);



#endif // __SOLUTION_H__
