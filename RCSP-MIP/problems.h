#ifndef __PROBLEMS_H__
#define __PROBLEMS_H__

#include <string_view>

/**
 * Defines for each problem an own problem type.
 * This problem type is used in generic algorithms.
 */

/* Node Constrained Shortest Path */
struct NCSP
{
  constexpr static const std::string_view name = "Node Constrained Shortest Path";
};

/* Task Constrained Shortest Path */
struct TCSP
{
	constexpr static const std::string_view name = "Task Constrained Shortest Path";
};

/* Resource Constrained Shortest Path */
struct RCSP
{
  constexpr static const std::string_view name = "Resource Constrained Shortest Path";
};


#endif // __PROBLEMS_H__
