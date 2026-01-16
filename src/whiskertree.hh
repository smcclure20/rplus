#ifndef WHISKERTREE_HH
#define WHISKERTREE_HH

#include <array>

#include "configrange.hh"
#include "whisker.hh"
#include "memoryrange.hh"
#include "dna.pb.h"

class WhiskerTree {
private:
  MemoryRange _domain;

  std::vector< WhiskerTree > _children;
  std::vector< Whisker > _leaf;

  const Whisker * whisker( const Memory & _memory ) const;

public:
  WhiskerTree();

  WhiskerTree( const std::vector< Axis > signals );

  WhiskerTree( const Whisker & whisker, const bool bisect );

  const Whisker & use_whisker( const Memory & _memory, const bool track ) const;
  int get_whisker_count( const Memory & _memory) const;

  void use_window( const unsigned int win ) const;

  bool replace( const Whisker & w );
  bool replace( const Whisker & src, const WhiskerTree & dst );
  const Whisker * most_used( const unsigned int max_generation ) const;
  int count_whiskers_in_gen ( const unsigned int max_generation ) const;

  void add_tree_counts( const WhiskerTree & tree);

  void reset_counts( void );
  void promote( const unsigned int generation );
  void reset_generation( void );

  std::string str( void ) const;
  std::string str( const unsigned int total ) const;
  unsigned int total_queries( void ) const;

  unsigned int num_children( void ) const;
  unsigned int total_whiskers( void ) const;

  bool is_leaf( void ) const;

  RemyBuffers::WhiskerTree DNA( void ) const;
  WhiskerTree( const RemyBuffers::WhiskerTree & dna );
};

#endif
