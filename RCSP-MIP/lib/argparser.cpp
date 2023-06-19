#include "argparser.h"

#include <iostream>
#include <fstream>

ArgParser::ArgParser(int argc, char *argv[]) : m_help_detected{false}
{
	args.reserve(argc);
	for (int i = 0; i < argc; i++) {
		args.emplace_back(argv[i]);
		if (args.back() == "-h")
			m_help_detected = true;
	}
}

bool ArgParser::isHelpSet() const
{
	return m_help_detected;
}

void ArgParser::help(std::ostream &os) const
{
	for (auto it = paras.begin(); it != paras.end(); ++it)
		it->second->help(os);
}

void ArgParser::parse()
{
	if (args.size()%2==0)
		throw std::runtime_error("Uneven number of parameters in command line");
	for (size_t i = 1; i < args.size(); i+=2) {
		std::string arg = removeHyphen(args[i]);
		if (arg.empty())
			throw std::runtime_error(std::string("Empty parameter: " + args[i]));
		if (arg == "@") {
			parse(args[i+1]);  // read args from file
		} else {
			auto it = paras.find(arg);
			if (it == paras.end())
				throw std::runtime_error(std::string("Unknown paramter: " + args[i]));
			it->second->set(args[i+1]);
		}
	}
}

void ArgParser::parse(const std::string &filename)
{
	std::ifstream file(filename);
	if (!file.is_open())
		throw std::runtime_error(std::string("Cannot open parameter file: ") + filename);

	std::string line;
	while (std::getline(file, line)) {
		if (line[0] == '#')
			continue;
		std::stringstream ss(line);
		std::string arg, value;
		ss >> arg;
		if (ss.fail())
			throw std::runtime_error(std::string("Cannot read argument name from file ") + filename);
		arg = removeHyphen(arg);
		if (arg.empty())
			throw std::runtime_error(std::string("Empty parameter: " + arg));
		auto it = paras.find(arg);
		if (it == paras.end())
			throw std::runtime_error(std::string("Unknown paramter: " + arg));
		ss >> value;
		if (ss.fail())
			throw std::runtime_error(std::string("Cannot read argument value from file ") + filename);
		it->second->set(value);
	}
}

std::string ArgParser::removeHyphen(std::string para) const
{
	auto it = para.begin();
	while (it != para.end()) {
		if (*it == '-')
			it = para.erase(it);
		else
			break;
	}
	return para;
}

std::ostream& operator<<(std::ostream& os, const ArgParser& parser)
{
	for (auto it = parser.paras.begin(); it != parser.paras.end(); ++it)
		it->second->print(os);
	return os;
}
