#ifndef EVALUATOR_HH
#define EVALUATOR_HH

#include <string>
#include <vector>
#include <future>

#include "random.hh"
#include "whiskertree.hh"
#include "fintree.hh"
#include "network.hh"
#include "problem.pb.h"
#include "answer.pb.h"

template <typename T>
class Evaluator
{
public:
  class Outcome
  {
  public:
    double score;
    std::vector<double> raw_scores;
    std::vector< std::pair< NetConfig, std::vector< std::pair< double, double > > > > throughputs_delays;
    T used_actions;

    Outcome() : score( 0 ), raw_scores(), throughputs_delays(), used_actions() {}

    Outcome( const AnswerBuffers::Outcome & dna );

    AnswerBuffers::Outcome DNA( void ) const;
  };

private:
  const unsigned int _prng_seed;
  unsigned int _tick_count;

  std::vector< NetConfig > _configs;

  ProblemBuffers::Problem _ProblemSettings_DNA ( void ) const;

  void _generate_configs( const ConfigRange & range );
  void _sample_configs(const ConfigRange & range, const int num);

  double _sample_range(double min, double max, double incr) { int index = rand() % (int)(floor((max - min) / incr) + 1); return min + (incr * index); };

public:
  Evaluator( const ConfigRange & range, const int sample = 0, const int seed = 0);
  
  ProblemBuffers::Problem DNA( const T & actions ) const;

  Outcome score( T & run_actions,
		const bool trace = false,
		const double carefulness = 1) const;

  static Evaluator::Outcome parse_problem_and_evaluate( const ProblemBuffers::Problem & problem );

  static Outcome score( T & run_actions,
			const unsigned int prng_seed,
			const std::vector<NetConfig> & configs,
			const bool trace,
			const unsigned int ticks_to_run );

  static Outcome score_config( T & run_actions,
      const unsigned int prng_seed,
      const NetConfig & config,
      const bool trace,
      const unsigned int ticks_to_run );

  Outcome score_parallel( T & run_actions,
      const bool trace = false, 
      const double carefulness = 1) const; 

  int num_configs(void) const { return _configs.size(); };

  std::vector< NetConfig > get_configs ( void ) const { return _configs; }; // TODO: how to make sure these are immutable
};

#endif
