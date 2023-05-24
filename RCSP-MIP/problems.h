#ifndef __PROBLEMS_H__
#define __PROBLEMS_H__

#include <string_view>

/**
 * Defines for each problem an own problem type.
 * This problem type is used in generic algorithms.
 */

/* Shortest Path */
struct SP
{
  constexpr static const std::string_view name = "Shortest Path";
};

/* Resource Constrained Shortest Path */
struct RCSP
{
  constexpr static const std::string_view name = "Resource Constrained Shortest Path";
};


#endif // __PROBLEMS_H__
