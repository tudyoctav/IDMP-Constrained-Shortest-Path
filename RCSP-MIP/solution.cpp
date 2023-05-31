#include "solution.h"

#include "lib/util.h"
#include "users.h"

#include <algorithm>
#include <numeric>
#include <cassert>



/*****************************************************************************************/
/** Node Constrained Shortest Path *******************************************************/
/*****************************************************************************************/
Solution<NCSP>::Solution(const Instance<NCSP>& inst) : shortest_path(inst.n)
{
  std::iota(shortest_path.begin(), shortest_path.end(), 0);
  total_cost = (int)inst.c.size();
}

std::ostream& operator<<(std::ostream& os, const Solution<NCSP>& sol)
{
  os << sol.shortest_path;
  return os;
}



/*****************************************************************************************/
/** Task Constrained Shortest Path *******************************************************/
/*****************************************************************************************/
Solution<TCSP>::Solution(const Instance<TCSP>& inst) : shortest_path(inst.n)
{
	std::iota(shortest_path.begin(), shortest_path.end(), 0);
	total_cost = (int)inst.c.size();
}

std::ostream& operator<<(std::ostream& os, const Solution<NCSP>& sol)
{
	os << sol.shortest_path;
	return os;
}



/*****************************************************************************************/
/** Resource Constrained Shortest Path ***************************************************/
/*****************************************************************************************/
Solution<RCSP>::Solution(const Instance<RCSP>& inst) : shortest_path(inst.n)
{
	std::iota(shortest_path.begin(), shortest_path.end(), 0);
	total_cost = (int)inst.c.size();
}

std::ostream& operator<<(std::ostream & os, const Solution<RCSP>&sol)
{
	os << sol.shortest_path;
	return os;
}


