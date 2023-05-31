#ifndef __LOG_H__
#define __LOG_H__

/**
 * Logging class adapted and simplified from
 *
 *   https://www.cppstories.com/2021/stream-logger/
 *   https://stackoverflow.com/questions/2212776/overload-handling-of-stdendl
 *
 * added color (ansi esc codes) support.
 */

#include <iostream>
#include <iomanip>
#include <string_view>


namespace logging {

enum Flags {
	L_clearFlags,
	L_concat,
	//L_time,
	L_endl,
	L_null = 4,
	L_cout = 8,
	L_tabs = 16,
};


struct AnsiEsc {
	enum Type { Color, Ignore, Reset, Other };
	explicit AnsiEsc(std::string_view ansi_code, Type t = Other) : code(ansi_code), type(t) { }
	std::string code;
	Type type;
};

extern AnsiEsc Black    ;
extern AnsiEsc Red      ;
extern AnsiEsc Green    ;
extern AnsiEsc Yellow   ;
extern AnsiEsc Blue     ;
extern AnsiEsc Magenta  ;
extern AnsiEsc Cyan     ;
extern AnsiEsc White    ;
extern AnsiEsc BgBlack  ;
extern AnsiEsc BgRed    ;
extern AnsiEsc BgGreen  ;
extern AnsiEsc BgYellow ;
extern AnsiEsc BgBlue   ;
extern AnsiEsc BgMagenta;
extern AnsiEsc BgCyan   ;
extern AnsiEsc BgWhite  ;
extern AnsiEsc ResetCol ;
extern AnsiEsc NoCol    ;

inline Flags operator +=(Flags& l_flag, Flags r_flag) { return l_flag = static_cast<Flags>(l_flag | r_flag); }
inline Flags operator -=(Flags& l_flag, Flags r_flag) { return l_flag = static_cast<Flags>(l_flag & ~r_flag); }

using Streamable = std::ostream;

class Log
{
public:
	Flags addFlag(Flags flag) { return _flags += flag; }
	Flags removeFlag(Flags flag) { return _flags -= flag; }
//	virtual void flush() { stream().flush(); _flags -= L_startWithFlushing; }
	virtual bool open() { return false; }

	template <typename T>
	Log& log(const T& value);

	template<template<typename> class T, typename X>
	Log& log(const T<X>& value);

	Log& operator <<(Flags);

	Log& operator << (decltype (&std::endl<char, std::char_traits<char>>)) {
		return *this << L_endl;
	}

	Log& operator << (decltype (std::hex) manip) {
		stream() << manip; return *this;
	}

	Log& operator << (decltype (std::setw) manip) {
		stream() << manip; return *this;
	}

	Log& operator << (const AnsiEsc& ansi) {
		if (is_null() || ansi.type == AnsiEsc::Ignore) return *this;
		stream() << ansi.code;
		if (ansi.type == AnsiEsc::Color)
			_color_is_active = true;
		else if (ansi.type == AnsiEsc::Reset)
			_color_is_active = false;
		return *this;
	}

	Log& activate(bool make_active = true) {
		if (make_active) _flags -= L_null;
		else             _flags += L_null;
		return *this;
	}

	virtual Streamable& stream();

	using ostreamPtr = Streamable*;
	virtual Log* mirror_stream(ostreamPtr& mirrorStream) { return this; }

protected:
	Log(Flags initFlag = L_null) : _flags{initFlag} {}
	Log(Flags initFlag = L_null, Streamable& = std::cout) : _flags{initFlag} {}

	//virtual Log& logTime();

	template<class T> friend Log& operator <<(Log& logger, const T& value);
	template<template<typename> class T, typename X> friend Log& operator<<(Log& logger, const T<X>& value);

	bool is_tabs() const { return _flags & L_tabs /* || has_time() */; }
	bool is_null() const { return _flags & L_null; }
	bool is_cout() const { return _flags == L_cout; }
	bool is_col()  const { return _color_is_active; }
	//bool has_time() const { return (_flags & 7) == L_time; }

	Flags _flags = L_clearFlags; //L_startWithFlushing;
	bool _color_is_active;  // if a color is active then the next std::endl will reset the color
};

template<typename T>
Log& operator <<(Log& logger, const T& value) {
	return logger.log(value);
}

template<template<typename> class T, typename X>
Log& operator<<(Log& logger, const T<X>& value) {
	return logger.log(value);
}

template<typename T>
Log& Log::log(const T& value) {
	if (is_null()) return *this;
	auto streamPtr = &stream();
	Log* logger = this;
	do {
		if (is_tabs())
			*streamPtr << "\t";
		(*streamPtr) << value;
		logger = logger->mirror_stream(streamPtr);
	} while (streamPtr);
	//removeFlag(L_time);
	return *this;
}

template<template<typename> class T, typename X>
Log& Log::log(const T<X>& value) {
	if (is_null()) return *this;
	auto streamPtr = &stream();
	Log* logger = this;
	do {
		if (is_tabs())
			*streamPtr << "\t";
		(*streamPtr) << value;
		logger = logger->mirror_stream(streamPtr);
	} while (streamPtr);
	//removeFlag(L_time);
	return *this;
}

class NullBuff : public std::streambuf
{
public:
	NullBuff() { setp(nullptr, nullptr); }
private:
	int_type overflow(int_type) override { return std::char_traits<char>::not_eof(0); }
} inline null_buff{};

inline Streamable null_ostream{ &null_buff };

inline Streamable& Log::stream() { return null_ostream; }

class ConLog : public Log
{
public:
	ConLog(Flags init_flags = L_null, Streamable& ostream = std::cout)
		: Log(init_flags, ostream), _ostream(&ostream)
	{
		ostream.flush();
	}

	Streamable& stream() override { return is_null() ? Log::stream() : *_ostream; }

	Log* mirror_stream(ostreamPtr& mirrorStream) override {
		if (mirrorStream == _ostream)
			mirrorStream = nullptr;
		else
			mirrorStream = _ostream;
		return this;
	}

protected:
	Streamable* _ostream = 0;
};

}

#endif // __LOG_H__
