#ifndef __UTIL_H__
#define __UTIL_H__

#include <iostream>
#include <iterator>
#include <vector>
#include <unordered_set>
#include <unordered_map>

#include "log.h"


template <typename T>
std::ostream& operator<< (std::ostream& out, const std::vector<T>& v)
{
  if ( !v.empty() )
  {
    out << '[';
    std::copy (v.begin(), v.end()-1, std::ostream_iterator<T>(out, ", "));
    out << v.back() << "]";
  }
  return out;
}

template <typename T>
logging::Log& operator<< (logging::Log& log, const std::vector<T>& v)
{
	log << '[';
	for (auto it = v.begin(); it != v.end(); ++it) {
		if (it != v.begin()) log << ", ";
		log << *it;
	}
	log <<']';
	return log;
}


template <typename T>
std::ostream& operator<< (std::ostream& out, const std::unordered_set<T>& s) 
{
  if ( !s.empty() )
  {
    out << '(';
    std::copy (s.begin(), s.end(), std::ostream_iterator<T>(out, ", "));
    out << ')';
  }
  return out;
}

template <typename K, typename V>
std::ostream& operator<< (std::ostream& out, const std::unordered_map<K,V>& m)
{
  if ( !m.empty() )
  {
    out << '[';
    for (auto it = m.begin(); it != m.end(); it++)
      out << '<' << it->first << ", " << it->second << '>';
    out << ']';
  }
  return out;
}

#endif // __UTIL_H__
