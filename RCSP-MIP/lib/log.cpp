#include "log.h"

using namespace logging;

Log& Log::operator<<(Flags flag) {
	if (is_null()) return *this;
	switch(flag) {
	case logging::L_concat:
		removeFlag(L_tabs);
		break;
	//case logging::L_time:
	//	logTime();
	//	break;
	case logging::L_endl: {
		auto streamPtr = &stream();
		Log* logger = this;
		do {
			if (is_col()) {
				*streamPtr << ResetCol.code;
				_color_is_active = false;
			}
			*streamPtr << std::endl;
			logger = logger->mirror_stream(streamPtr);
		} while(streamPtr);
	}
	default:
		addFlag(flag);
	}
	return *this;
}
/*
Log& Log::logTime() {
	std::time_t now = std::time(nullptr);
	auto localTime = std::localtime(&now);
	*this << std::put_time(localTime, "%d/%m/%y %H:%M:%S");
	_flags += L_time;
	return *this;
}
*/

namespace logging {
/*
		 foreground background
black        30         40
red          31         41
green        32         42
yellow       33         43
blue         34         44
magenta      35         45
cyan         36         46
white        37         47

\033[<x>m

*/
AnsiEsc Black    ("\033[1;30m", AnsiEsc::Color);
AnsiEsc Red      ("\033[1;31m", AnsiEsc::Color);
AnsiEsc Green    ("\033[1;32m", AnsiEsc::Color);
AnsiEsc Yellow   ("\033[1;33m", AnsiEsc::Color);
AnsiEsc Blue     ("\033[1;34m", AnsiEsc::Color);
AnsiEsc Magenta  ("\033[1;35m", AnsiEsc::Color);
AnsiEsc Cyan     ("\033[1;36m", AnsiEsc::Color);
AnsiEsc White    ("\033[1;37m", AnsiEsc::Color);
AnsiEsc BgBlack  ("\033[1;40m", AnsiEsc::Color);
AnsiEsc BgRed    ("\033[1;41m", AnsiEsc::Color);
AnsiEsc BgGreen  ("\033[1;42m", AnsiEsc::Color);
AnsiEsc BgYellow ("\033[1;43m", AnsiEsc::Color);
AnsiEsc BgBlue   ("\033[1;44m", AnsiEsc::Color);
AnsiEsc BgMagenta("\033[1;45m", AnsiEsc::Color);
AnsiEsc BgCyan   ("\033[1;46m", AnsiEsc::Color);
AnsiEsc BgWhite  ("\033[1;47m", AnsiEsc::Color);
AnsiEsc ResetCol ("\033[0m", AnsiEsc::Reset);
AnsiEsc NoCol    ("", AnsiEsc::Ignore);
}

