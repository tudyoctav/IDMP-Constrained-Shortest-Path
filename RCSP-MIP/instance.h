#ifndef __INSTANCE_H__
#define __INSTANCE_H__


#include <string>
#include <vector>
#include <utility>
#include <iostream>

#include "problems.h"


template<typename>
struct Solution;


/*
 * Generic problem instance class.
 * To write an instance class for a specific problem,
 * specialize this class for the corresponding problem type.
 */
template<typename ProbT>
struct Instance { };




/*****************************************************************************************/
/** Node Constrained Shortest Path *******************************************************/
/*****************************************************************************************/
template<>
struct Instance<NCSP>
{
	friend std::ostream& operator<<(std::ostream& os, const Instance<NCSP>& inst);

	Instance(const std::string& input_file);

	int objective(const Solution<NCSP>& sol) const;

	std::string filename;

	int n; // number of nodes
	int s; // starting node
	int t; // target node 

	std::vector<int> V;					 // index set of vertices [0,...,n-1]
	std::vector<std::pair<int, int> > A; // index set of arcs (i, j) in A
	std::vector<std::vector<int> > c;    // cost of arcs c(i, j)
	std::vector<int> p;					 // penalty of node p(j)
};

std::ostream& operator<<(std::ostream& os, const Instance<NCSP>& inst);




/*****************************************************************************************/
/** Task Constrained Shortest Path *******************************************************/
/*****************************************************************************************/
template<>
struct Instance<TCSP>
{
	friend std::ostream& operator<<(std::ostream& os, const Instance<TCSP>& inst);

	Instance(const std::string& input_file);

	int objective(const Solution<TCSP>& sol) const;

	std::string filename;

	int n; // number of nodes
	int s; // starting node
	int t; // target node 

	std::vector<int> V;					 // index set of vertices [0,...,n-1]
	std::vector<std::pair<int, int> > A; // index set of arcs (i, j) in A
	std::vector<std::vector<int> > c;    // cost of arcs c(i, j)
	std::vector<std::vector<int> > T;	 // task set of node i includes j
};

std::ostream& operator<<(std::ostream& os, const Instance<TCSP>& inst);




/*****************************************************************************************/
/** Resource Constrained Shortest Path ***************************************************/
/*****************************************************************************************/
template<>
struct Instance<RCSP>
{
	friend std::ostream& operator<<(std::ostream& os, const Instance<RCSP>& inst);

	Instance(const std::string& input_file);

	int objective(const Solution<RCSP>& sol) const;

	std::string filename;

	int n; // number of nodes
	int s; // starting node
	int t; // target node 

	std::vector<int> V; 				 // index set of nodes [0,...,n-1]
	std::vector<std::pair<int, int> > R; // constraints {l, u} on node i
	std::vector<std::pair<int, int> > A; // index set of arcs {i, j} in A
	std::vector<std::vector<int> > c;    // cost of arcs c(i, j)
	std::vector<std::vector<int> > d;    // distance of arcs d(i, j)
};

std::ostream& operator<<(std::ostream& os, const Instance<RCSP>& inst);


#endif // __INSTANCE_H__
