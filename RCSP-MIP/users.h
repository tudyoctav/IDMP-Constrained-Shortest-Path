#ifndef USERS_H
#define USERS_H

#include "lib/log.h"

// Verbosity levels
#define TRACE (6)
#define DBG   (5)
#define INFO  (4)
#define WARN  (3)
#define ERROR (2)
#define FATAL (1)

// This file is not included in the repository.
// Create your own file if you want to see stdout output from different users/modules
#ifndef NO_PRIVATE
#define USER_MIP  DBG
#endif

namespace user {

#define CREATE_USER(x, col, v) struct x { inline const static std::string name = #x; inline const static int verbosity = (v); inline const static logging::AnsiEsc& color = col; }

// provides access to looger of user UserT
template<typename UserT>
logging::Log & logger() {
	static logging::ConLog mylog{logging::L_clearFlags};
	return mylog;
}


// decoration logger -> add user name and color
template <typename UserT>
logging::Log& dec_logger(int verbosity = DBG) {
	return user::logger<UserT>().activate(UserT::verbosity >= verbosity) << UserT::name << ": " << UserT::color;
}


// null logger for user UserT
template <typename  UserT>
logging::Log& null_logger() {
	static logging::ConLog mylog{};
	mylog.activate(false);
	return mylog;
}

/********************************************************************/
/* TEMPLATE                                                         */
/********************************************************************/
/* Define for each programmer/submodule XX an own compiler switch
 * USER_XX to turn user/submodule specific outputs on or off.
 * To turn output on, define in your OWN private.h file the
 * corresponding USER_XX macros.
 * The defined number of USER_XX indicates the verbosity level.
 * If the level is high than more output will be printed to the stream.
 * Below you see a template to define a user. Replace the XX by the
 * user's name. Furthermore you can choose a color for the user,
 * see log.h for a color list.
 */

/*
#if defined(USER_XX) && (USER_XX > 0)
CREATE_USER(XX, logging::Blue, USER_XX);
#define XX_OUT(verbosity) if (true) user::dec_logger<user::XX>(verbosity)
#else
CREATE_USER(XX, logging::White, 0);
#define XX_OUT(verbosity) if (false) user::null_logger<user::XX>()
#endif
*/


// Standard output is always defined
CREATE_USER(STD, logging::NoCol, TRACE);
#define SOUT() user::logger<user::STD>()


// Jeroen Groenheide
#if defined(USER_JG) && (USER_JG > 0)
CREATE_USER(JG, logging::Blue, USER_JG);
#define JG_OUT(verbosity) if (true) user::dec_logger<user::JG>(verbosity)
#else
CREATE_USER(JG, logging::NoCol, 0);
#define JG_OUT(verbosity) if (false) user::null_logger<user::JG>()
#endif


// Mixed Integer Programming
#if defined(USER_MIP) && (USER_MIP > 0)
CREATE_USER(MIP, logging::Green, USER_MIP);
#define MIP_OUT(verbosity) if (true) user::dec_logger<user::MIP>(verbosity)
#else
CREATE_USER(MIP, logging::NoCol, 0);
#define MIP_OUT(verbosity) if (false) user::null_logger<user::MIP>()
#endif

}

#endif // USERS_H
