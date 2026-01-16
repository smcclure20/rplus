#include <utility>

#include "link.hh"

using namespace std;

template <class NextHop>
void Link::tick( NextHop & next, const double & tickno )
{
  _pending_packet.tick( next, tickno );

  if ( _pending_packet.empty() ) {

    if ( not _buffer.empty() ) {
      Packet p = _buffer.front();
      _buffer.pop_front();
      add_packet_to_counter(tickno);
      set_int_fields(p);
      _pending_packet.accept( p, tickno );
    }
  }
}
