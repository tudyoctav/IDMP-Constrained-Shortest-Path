#ifndef ARGPARSER_H
#define ARGPARSER_H

/**
 * Class ArgParser is used to parse command line arguments.
 * It is a very simple implementation that only supports optional arguments with exactly one parameter yet.
 * Therefore the number of arguments must always be uneven (2 * (arguments + parameter) + one program name).
 * Converts to basic datatypes like int, long, float, double, ... and std::string.
 */

#include <string>
#include <map>
#include <vector>
#include <sstream>
#include <memory>
#include <any>
#include <stdexcept>


class ArgParser
{
private:
	class AbstractArgument
	{
	public:
		AbstractArgument(const std::string& name, const std::string& desc)
			: m_name(name), m_desc(desc)
		{ }
		virtual void set(const std::string& para) = 0;
		virtual std::any get() const = 0;
		virtual void help(std::ostream& os) const = 0;   // print help: para name, default value, desciption
		virtual void print(std::ostream& os) const = 0;  // print para name and para value
		const std::string& name() const { return m_name; }
		const std::string& description() const { return m_desc; }
	private:
		std::string m_name;
		std::string m_desc;
	};

	template<typename T>
	class Argument : public AbstractArgument
	{
	public:
		Argument(const std::string& name, const std::string& desc, T default_value) : AbstractArgument(name, desc), m_default_value(default_value), m_value(default_value)
		{ }
		void set(const std::string& para) override
		{
			std::stringstream ss(para);
			ss >> m_value;
			if (ss.fail())
				throw std::runtime_error(std::string("Invalid value ") + para + std::string(" for parameter ") + name());
		}
		std::any get() const override { return m_value; }
		void help(std::ostream& os) const override { os << name() << "\t(" << m_default_value << ") " << description() << std::endl; }
		void print(std::ostream& os) const override { os << name() << "\t" << m_value << std::endl; }
		T value() const { return m_value; }
		T defaultValue() const { return m_default_value; }
	private:
		T m_default_value;
		T m_value;
	};

	template<typename T>
	class RangeArgument : public Argument<T>
	{
	public:
		using Argument<T>::name;
		using Argument<T>::description;
		using Argument<T>::set;
		using Argument<T>::value;
		using Argument<T>::defaultValue;
		RangeArgument(const std::string& name, const std::string& desc, T default_value, T min_value, T max_value)
			: Argument<T>(name, desc, default_value), m_min_value(min_value), m_max_value(max_value)
		{ }
		void set(const std::string& para) override
		{
			Argument<T>::set(para);
			if (value() < m_min_value || value() > m_max_value)
				throw std::runtime_error(std::string("Invalid value ") + para + std::string(" for parameter ") + name());
		}
		void help(std::ostream& os) const override { os << name() << "\t(" << defaultValue() << ") [" << m_min_value << "," << m_max_value << "] " << description() << std::endl; }
	private:
		T m_min_value;
		T m_max_value;
	};

	template<typename T>
	class OptionArgument : public Argument<T>
	{
	public:
		using Argument<T>::name;
		using Argument<T>::description;
		using Argument<T>::set;
		using Argument<T>::value;
		using Argument<T>::defaultValue;
		OptionArgument(const std::string& name, const std::string& desc, T default_value, std::vector<T> options)
			: Argument<T>(name, desc, default_value), m_options(options)
		{ }
		void set(const std::string& para) override
		{
			Argument<T>::set(para);
			auto it = std::find(m_options.begin(), m_options.end(), value());
			if (it == m_options.end())
				throw std::runtime_error(std::string("Invalid value ") + para + std::string(" for parameter ") + name());
		}
		void help(std::ostream& os) const override { os << name() << "\t(" << defaultValue() << ") " << m_options << " "<< description() << std::endl; }
	private:
		std::vector<T> m_options;
	};


public:
	ArgParser(int argc, char* argv[]);

	ArgParser(const ArgParser&) = delete;

	/*
	 *  Add an argument of type T with name <name> and description <desc> to the ArgParser object.
	 */
	template<typename T>
	void add(const std::string& name, const std::string& desc, T default_value)
	{
		paras.insert(std::make_pair(name, std::unique_ptr<AbstractArgument>(new Argument<T>(name, desc, default_value))));
	}

	/*
	 *  Add an argument of type T with name <name> and description <desc> to the ArgParser object.
	 *  The parsed parameter form the command line must be between min_value and max_value. If this is not the case
	 *  then the method parse will throw a std::runtime_error exception.
	 */
	template<typename T>
	void add(const std::string& name, const std::string& desc, T default_value, T min_value, T max_value)
	{
		paras.insert(std::make_pair(name, std::unique_ptr<AbstractArgument>(new RangeArgument<T>(name, desc, default_value, min_value, max_value))));
	}

	/*
	 *  Add an argument of type T with name <name> and description <desc> to the ArgParser object.
	 *  The parsed parameter form the command line must be a value given by <options>. If this is not the case
	 *  then the method parse will throw a std::runtime_error exception.
	 */
	template<typename T>
	void add(const std::string& name, const std::string& desc, T default_value, const std::vector<T>& options)
	{
		paras.insert(std::make_pair(name, std::unique_ptr<AbstractArgument>(new OptionArgument<T>(name, desc, default_value, options))));
	}

	/*
	 * Returns the parameter of argument <name>.
	 * If the argument had not been added before by one of the add methods then a std::runtime_error exception will be thrown.
	 */
	template<typename T>
	T get(const std::string& name) {
		auto it = paras.find(name);
		if (it == paras.end())
			throw std::runtime_error(std::string("Unknown argument: " + name));
		return std::any_cast<T>(it->second->get());
	}

	bool isHelpSet() const;             // Returns true if -h was parsed.
	void help(std::ostream& os) const;  // Print help

	void parse();  // Parse all arguments from the command line. Throws std::runtime_error if an argument is unknown or can not be converted to a specific type.

	void parse(const std::string& filename); // reads parameters from file <filename>

	/*
	 * Prints all arguments + parameters.
	 */
	friend std::ostream& operator<<(std::ostream& os, const ArgParser& parser);

protected:
	std::string removeHyphen(std::string para) const;  // help method to remove "-" and "--" from arguments.

private:
	std::vector<std::string> args;
	std::map<std::string, std::unique_ptr<AbstractArgument> > paras;
	bool m_help_detected;
};


#endif // ARGPARSER_H
