#include <string>
#include <cstdio>
#include <sys/stat.h>
#include <fcntl.h>

#include "whiskertree.hh"
using namespace std;

int main( int argc, char *argv[] )
{
  if ( argc != 2 ) {
    cerr << "This tool prints the whiskers of a simulations data file." << endl;
    cerr << "There must be exactly one argument, the name of the simulations data file." << endl;
    exit( 1 );
  }

  string filename( argv[1] );
  int fd = open( filename.c_str(), O_RDONLY );
  if ( fd < 0 ) {
    perror( "open" );
    exit( 1 );
  }

  RemyBuffers::WhiskerTree tree;
  if ( !tree.ParseFromFileDescriptor( fd ) ) {
    fprintf( stderr, "Could not parse %s.\n", filename.c_str() );
    exit( 1 );
  }
  WhiskerTree whiskers = WhiskerTree( tree );  

  if ( close( fd ) < 0 ) {
    perror( "close" );
    exit( 1 );
  }

  cout << whiskers.str() << endl;
  return 0;
}