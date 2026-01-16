#include <iostream>
#include <chrono>

#include "ratbreeder.hh"

using namespace std;

Evaluator< WhiskerTree >::Outcome RatBreeder::improve( WhiskerTree & whiskers )
{
  /* back up the original whiskertree */
  /* this is to ensure we don't regress */
  WhiskerTree input_whiskertree( whiskers );

  /* evaluate the whiskers we have */
  whiskers.reset_generation();
  unsigned int generation = 0;

  while ( generation < 5 ) {
    const Evaluator< WhiskerTree > eval( _options.config_range, _whisker_options.sample_size );

    printf("Generation: %d, whiskers in generation: %d\n", generation, whiskers.count_whiskers_in_gen(generation));
    printf("Finding most used whisker...\n");
    auto start = std::chrono::system_clock::now();
    auto outcome( eval.score( whiskers, false, 1 ) );
    auto end = std::chrono::system_clock::now();
    std::chrono::duration<double> elapsed_seconds = end-start;
    std::cout << "elapsed time: " << elapsed_seconds.count() << "s" << std::endl;

    /* is there a whisker at this generation that we can improve? */
    printf("Done evaluating.\n");
    auto most_used_whisker_ptr = outcome.used_actions.most_used( generation );

    /* if not, increase generation and promote all whiskers */
    if ( !most_used_whisker_ptr ) {
      generation++;
      whiskers.promote( generation );

      continue;
    }

    WhiskerImprover improver( eval, whiskers, _whisker_options, outcome.score );

    Whisker whisker_to_improve = *most_used_whisker_ptr;

    double score_to_beat = outcome.score;

    printf("Improving (%d)...\n", generation);
    while ( 1 ) {
      double new_score = improver.improve( whisker_to_improve );
      assert( new_score >= score_to_beat );
      if ( new_score == score_to_beat ) {
          cerr << "Ending search." << endl;
          break;
      } else {
          cerr << "Score jumps from " << score_to_beat << " to " << new_score << endl;
          score_to_beat = new_score;
      }
    }

    whisker_to_improve.demote( generation + 1 );

    const auto result __attribute((unused)) = whiskers.replace( whisker_to_improve );
    assert( result );
  }

  printf("Splitting most used whisker\n");
  /* Split most used whisker */
  apply_best_split( whiskers, generation, _whisker_options.sample_size );

  /* carefully evaluate what we have vs. the previous best */
  printf("Performing careful eval to avoid regression...\n");
  const Evaluator< WhiskerTree > eval2( _options.config_range, _whisker_options.sample_size * 10 ); 
  const auto new_score = eval2.score_parallel( whiskers, false, 10);
  const auto old_score = eval2.score_parallel( input_whiskertree, false, 10);

  if ( old_score.score > new_score.score ) {
    fprintf( stderr, "Regression, old=%f, new=%f\n", old_score.score, new_score.score );
    whiskers = input_whiskertree;
    return old_score;
  }

  return new_score;
}

vector< Whisker > WhiskerImprover::get_replacements( Whisker & whisker_to_improve ) 
{
  return whisker_to_improve.next_generation( _options.optimize_window_increment,
                                             _options.optimize_window_multiple,
                                             _options.optimize_intersend,
                                             _options.alternates_limit );
}
