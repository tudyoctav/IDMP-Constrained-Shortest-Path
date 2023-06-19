#ifndef __LU_TZE_H__
#define __LU_TZE_H__

#include <vector>

class LuTze
{
  public:
	// starts time measurement, returns ticket
	static int start()
	{
		int ticket;
		if (m_free_tickets.empty()) {
			ticket = m_max_ticket_number++;
			m_tickets.push_back(0);
		} else {
			ticket = m_free_tickets.back();
			m_free_tickets.pop_back();
		}

		m_tickets[ticket] = cpu_time();

		return ticket;
	}

	// restarts time measurement, set start time for ticket to current CPU time
	static void restart(int ticket)
	{
		m_tickets[ticket] = cpu_time();
	}

	// returns number of CPU seconds since start was called, ticket is removed
	static double end(int ticket)
	{
		double t2 = cpu_time();
		double t1 = m_tickets[ticket];

		m_free_tickets.push_back(ticket);
		return t2 - t1;
	}

	// returns number of CPU seconds since start was called, ticket can be used further
	static double split_time(int ticket)
	{
		return cpu_time() - m_tickets[ticket];
	}

	// returns CPU time in seconds since the process was started
	static double cpu_time();

  private:
	static int m_max_ticket_number;
	static std::vector<double> m_tickets;  // stores start time for each ticket
	static std::vector<int> m_free_tickets;  // tickets that are currently not used
};

#endif  // __LU_TZE_H__
