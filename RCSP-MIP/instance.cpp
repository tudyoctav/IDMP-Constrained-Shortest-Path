#include "instance.h"
#include "solution.h"
#include "lib/util.h"
#include "users.h"

#include <fstream>
#include <sstream>
#include <stdexcept>
#include <algorithm>
#include <numeric>
#include <math.h>
#include <cassert>
#include <utility>



/*************************************************************************************************/
/* SP ********************************************************************************************/
/*************************************************************************************************/
Instance<NCSP>::Instance(const std::string& input_file) : filename(input_file)
{
	std::ifstream file(input_file);
	if (!file.is_open())
		throw std::runtime_error("Cannot open file!");

	int m; // number of arcs
	file >> m >> n >> s >> t;

	A.reserve(m);
	c.assign(n, std::vector<int>(n));
	for (int k = 0; k < m; k++) {
		int i, j; file >> i >> j;
		A.push_back({ i, j });
		file >> c[i][j];
	}

	V.reserve(n);
	p.assign(n, 0);
	for (int i = 0; i < n; i++) {
		V.push_back(i);
		file >> p[i];
	}
}

int Instance<NCSP>::objective(const Solution<NCSP>& sol) const
{
	return sol.total_cost;
}


std::ostream& operator<<(std::ostream& os, const Instance<NCSP>& inst)
{
	os << "m=" << inst.A.size() << ", n=" << inst.n << ", s=" << inst.s << ", t=" << inst.t;
	return os;
}



/*************************************************************************************************/
/* RCSP ******************************************************************************************/
/*************************************************************************************************/
Instance<RCSP>::Instance(const std::string& input_file) : filename(input_file)
{
	std::ifstream file(input_file);
	if (!file.is_open())
		throw std::runtime_error("Cannot open file!");

	int m; // number of arcs
	file >> m >> n >> s >> t;

	A.reserve(m);
	c.assign(n, std::vector<int>(n));
	d.assign(n, std::vector<int>(n));
	for (int k = 0; k < m; k++) {
		int i, j; file >> i >> j;
		file >> c[i][j] >> d[i][j];
		A.push_back({ i, j });
	}

	V.reserve(n);
	R.reserve(n);
	for (int i = 0; i < n; i++) {
		V.push_back(i);
		std::pair<int, int> b;
		file >> b.first >> b.second;
		R.push_back(b);
	}		
}

int Instance<RCSP>::objective(const Solution<RCSP>&sol) const
{
	return sol.total_cost;
}


std::ostream& operator<<(std::ostream & os, const Instance<RCSP>&inst)
{
	os << "m=" << inst.A.size() << ", n=" << inst.n << ", s=" << inst.s << ", t=" << inst.t;
	return os;
}

