#include "solution.h"

#include "lib/util.h"
#include "users.h"

#include <algorithm>
#include <numeric>
#include <cassert>



/*****************************************************************************************/
/** Shortest Path Problem ****************************************************************/
/*****************************************************************************************/
Solution<SP>::Solution(const Instance<SP>& inst) : shortest_path(inst.n)
{
  std::iota(shortest_path.begin(), shortest_path.end(), 0);
  total_cost = (int)inst.c.size();
}

std::ostream& operator<<(std::ostream& os, const Solution<SP>& sol)
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


