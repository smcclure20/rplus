#include <cstdio>
#include <vector>
#include <string>
#include <limits>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <iostream>
#include <fstream>

#include "evaluator.hh"
#include "configrange.hh"
#include "whiskertree.hh"
using namespace std;

template <typename T>
void print_tree(T & tree)  // go to file if there is an OF, otherwise stdout
{
  if ( tree.has_config() ) {
    printf( "Prior assumptions:\n%s\n\n", tree.config().DebugString().c_str() );
  }

  if ( tree.has_optimizer() ) {
    printf( "Remy optimization settings:\n%s\n\n", tree.optimizer().DebugString().c_str() );
  }
}

template <typename T>
void parse_outcome( T & outcome, bool verb ) 
{
  printf( "score = %f\n", outcome.score );
  

  double filtered_score = 0;
  int run_count = 0;
  if (outcome.score < 0) {
    for (auto &raw_score : outcome.raw_scores)
    {
      if (raw_score > 0)
      {
        filtered_score += raw_score;
        run_count ++;
      }
    }
    printf("filtered score: %f\n", filtered_score);
    printf("number  runs: %d\n", run_count);
  }

  double norm_score = 0;
  if (verb)
  {
      int i = 0;
      for ( auto &run : outcome.throughputs_delays ) {
        printf( "===\nconfig: %s\n", run.first.str().c_str() );
        printf( "score: %f\n", outcome.raw_scores.at(i));
        for ( auto &x : run.second ) {
          printf( "sender: [tp=%f, del=%f] (tpr=%f, delr=%f)\n", x.first, x.second, x.first / run.first.link_ppt, x.second / run.first.delay );
          norm_score += log2( x.first / run.first.link_ppt ) - log2( x.second / run.first.delay );
        }
        i++;
      }
  }

  printf( "normalized_score = %f\n", norm_score );
}

int main( int argc, char *argv[] )
{
  WhiskerTree whiskers;
  FinTree fins;
  bool is_poisson = false;
  unsigned int num_senders = 1;
  double link_ppt = 3.5;
  double delay = 20;
  double mean_on_duration = 1000.0;
  double mean_off_duration = 100.0;
  // double buffer_size = 250;
  double buffer_size = numeric_limits<unsigned int>::max();
  double stochastic_loss_rate = 0.001;
  unsigned int simulation_ticks = 10000;
  bool is_range = false;
  RemyBuffers::ConfigRange input_config;
  string config_filename;
  string output_filename;
  bool verbose = false;
  int default_sample_num = 100;
  int seed = time(NULL);

  for ( int i = 1; i < argc && !is_poisson; i++ ) {
    string arg( argv[ i ] );
    if ( arg.substr( 0, 7) == "sender=" ) {
        string sender_type( arg.substr( 7 ) );
        if ( sender_type == "poisson" ) {
          is_poisson = true;
          fprintf( stderr, "Running poisson sender\n" );
        }
    } 
  }
  for ( int i = 1; i < argc; i++ ) {
     string arg( argv[ i ] );
     if ( arg.substr( 0, 3 ) == "if=" ) {
      string filename( arg.substr( 3 ) );
      int fd = open( filename.c_str(), O_RDONLY );
      if ( fd < 0 ) {
        perror( "open" );
        exit( 1 );
      }

      if ( is_poisson ) {
        RemyBuffers::FinTree tree;
        if ( !tree.ParseFromFileDescriptor( fd ) ) {
          fprintf( stderr, "Could not parse %s.\n", filename.c_str() );
          exit( 1 );
        }
        print_tree< RemyBuffers::FinTree >(tree);
        fins = FinTree( tree );
      } else {
        RemyBuffers::WhiskerTree tree;
        if ( !tree.ParseFromFileDescriptor( fd ) ) {
          fprintf( stderr, "Could not parse %s.\n", filename.c_str() );
          exit( 1 );
        }
        print_tree< RemyBuffers::WhiskerTree >(tree);
        whiskers = WhiskerTree( tree );  
      }

      if ( close( fd ) < 0 ) {
        perror( "close" );
        exit( 1 );
      }
    } else if ( arg.substr( 0, 4 ) == "cfg=" ) {
      is_range = true;
      config_filename = string( arg.substr( 4 ) );
      int cfd = open( config_filename.c_str(), O_RDONLY );
      if ( cfd < 0 ) {
        perror( "open config file error");
        exit( 1 );
      }
      if ( !input_config.ParseFromFileDescriptor( cfd ) ) {
        fprintf( stderr, "Could not parse input config from file %s. \n", config_filename.c_str() );
        exit ( 1 );
      }
      if ( close( cfd ) < 0 ) {
        perror( "close" );
        exit( 1 );
      }
    } else if ( arg.substr( 0, 5 ) == "nsrc=" ) {
      num_senders = atoi( arg.substr( 5 ).c_str() );
      fprintf( stderr, "Setting num_senders to %d\n", num_senders );
    } else if ( arg.substr( 0, 5 ) == "link=" ) {
      link_ppt = atof( arg.substr( 5 ).c_str() );
      fprintf( stderr, "Setting link packets per ms to %f\n", link_ppt );
    } else if ( arg.substr( 0, 4 ) == "rtt=" ) {
      delay = atof( arg.substr( 4 ).c_str() );
      fprintf( stderr, "Setting delay to %f ms\n", delay );
    } else if ( arg.substr( 0, 3 ) == "on=" ) {
      mean_on_duration = atof( arg.substr( 3 ).c_str() );
      fprintf( stderr, "Setting mean_on_duration to %f ms\n", mean_on_duration );
    } else if ( arg.substr( 0, 4 ) == "off=" ) {
      mean_off_duration = atof( arg.substr( 4 ).c_str() );
      fprintf( stderr, "Setting mean_off_duration to %f ms\n", mean_off_duration );
    } else if ( arg.substr( 0, 4 ) == "buf=" ) {
      if (arg.substr( 4 ) == "inf") {
        buffer_size = numeric_limits<unsigned int>::max();
      } else {
        buffer_size = atoi( arg.substr( 4 ).c_str() );
      }
    } else if ( arg.substr( 0, 6 ) == "sloss=" ) {
      stochastic_loss_rate = atof( arg.substr( 6 ).c_str() );
      fprintf( stderr, "Setting stochastic loss rate to %f\n", stochastic_loss_rate );
    }
    
    else if ( arg.substr( 0, 5 ) == "seed=" ) {
      seed = atoi( arg.substr( 5 ).c_str() );
      fprintf( stderr, "Setting seed to %d \n", seed );
    }
    else if ( arg.substr( 0, 7 ) == "sample=" ) {
      default_sample_num = atoi( arg.substr( 7 ).c_str() );
      fprintf( stderr, "Setting sample size to %d \n", default_sample_num );
    }

    else if (arg.substr(0, 2) == "-v") {
      verbose = true;
    }
  }
  
  srand(seed);

  ConfigRange configuration_range;
  int sample_num = 0;
  if ( !is_range ) {
    configuration_range.link_ppt = Range( link_ppt, link_ppt, 0 ); /* 1 Mbps to 10 Mbps */
    configuration_range.rtt = Range( delay, delay, 0 ); /* ms */
    configuration_range.num_senders = Range( num_senders, num_senders, 0 );
    configuration_range.mean_on_duration = Range( mean_on_duration, mean_on_duration, 0 );
    configuration_range.mean_off_duration = Range( mean_off_duration, mean_off_duration, 0 );
    configuration_range.buffer_size = Range( buffer_size, buffer_size, 0 );
    configuration_range.stochastic_loss_rate = Range( stochastic_loss_rate, stochastic_loss_rate, 0);
    configuration_range.simulation_ticks = simulation_ticks;
  }
  else {
    configuration_range = ConfigRange( input_config );
    sample_num = default_sample_num;
  }

  if ( is_poisson ) {
    Evaluator< FinTree > eval( configuration_range );
    auto outcome = eval.score( fins, false, 10 );
    parse_outcome< Evaluator< FinTree >::Outcome > ( outcome, verbose);
  } else {
    
    printf("Number of rules in the tree: %d\n", whiskers.total_whiskers());
    Evaluator< WhiskerTree > eval( configuration_range, sample_num, seed );
    auto outcome = eval.score( whiskers, false, 1);
    parse_outcome< Evaluator< WhiskerTree >::Outcome > ( outcome, verbose );
  }

  return 0;
}
