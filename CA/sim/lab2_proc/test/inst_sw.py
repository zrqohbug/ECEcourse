#=========================================================================
# sw
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 0x00002000
    csrr x2, mngr2proc < 0xdeadbeef
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sw   x2, 0(x1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    lw   x3, 0(x1)
    csrw proc2mngr, x3 > 0xdeadbeef

    .data
    .word 0x01020304
  """

#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------

def gen_dest_dep_test():
  return [

    gen_st_dest_dep_test( 5, "sw", 0x2000, 0x00010203 ),
    gen_st_dest_dep_test( 4, "sw", 0x2004, 0x04050607 ),
    gen_st_dest_dep_test( 3, "sw", 0x2008, 0x08090a0b ),
    gen_st_dest_dep_test( 2, "sw", 0x200c, 0x0c0d0e0f ),
    gen_st_dest_dep_test( 1, "sw", 0x2010, 0x10111213 ),
    gen_st_dest_dep_test( 0, "sw", 0x2014, 0x14151617 ),

    gen_word_data([
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
    ])

  ]

#-------------------------------------------------------------------------
# gen_base_dep_test
#-------------------------------------------------------------------------

def gen_base_dep_test():
  return [

    gen_st_base_dep_test( 5, "sw", 0x2000, 0x00010203 ),
    gen_st_base_dep_test( 4, "sw", 0x2004, 0x04050607 ),
    gen_st_base_dep_test( 3, "sw", 0x2008, 0x08090a0b ),
    gen_st_base_dep_test( 2, "sw", 0x200c, 0x0c0d0e0f ),
    gen_st_base_dep_test( 1, "sw", 0x2010, 0x10111213 ),
    gen_st_base_dep_test( 0, "sw", 0x2014, 0x14151617 ),

    gen_word_data([
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
    ])

  ]

#-------------------------------------------------------------------------
# gen_base_eq_dep_test
#-------------------------------------------------------------------------

def gen_base_eq_dep_test():
  return [

    gen_st_base_eq_dest_test( "sw", 0x2000, 0x00010203 ),
    gen_st_base_eq_dest_test( "sw", 0x2004, 0x04050607 ),
    gen_st_base_eq_dest_test( "sw", 0x2008, 0x08090a0b ),
    gen_st_base_eq_dest_test( "sw", 0x200c, 0x0c0d0e0f ),
    gen_st_base_eq_dest_test( "sw", 0x2010, 0x10111213 ),
    gen_st_base_eq_dest_test( "sw", 0x2014, 0x14151617 ),

    gen_word_data([
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
    ])

  ]

#-------------------------------------------------------------------------
# gen_data_dep_test
#-------------------------------------------------------------------------

def gen_data_dep_test():
  return [

    gen_st_data_dep_test( 5, "sw", 0x2000, 0x00010203 ),
    gen_st_data_dep_test( 4, "sw", 0x2004, 0x04050607 ),
    gen_st_data_dep_test( 3, "sw", 0x2008, 0x08090a0b ),
    gen_st_data_dep_test( 2, "sw", 0x200c, 0x0c0d0e0f ),
    gen_st_data_dep_test( 1, "sw", 0x2010, 0x10111213 ),
    gen_st_data_dep_test( 0, "sw", 0x2014, 0x14151617 ),

    gen_word_data([
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
    ])

  ]

#-------------------------------------------------------------------------
# gen_data_eq_dep_test
#-------------------------------------------------------------------------

def gen_data_eq_dep_test():
  return [

    gen_st_data_eq_dest_test( "sw", 0x2000, 0x00010203 ),
    gen_st_data_eq_dest_test( "sw", 0x2004, 0x04050607 ),
    gen_st_data_eq_dest_test( "sw", 0x2008, 0x08090a0b ),
    gen_st_data_eq_dest_test( "sw", 0x200c, 0x0c0d0e0f ),
    gen_st_data_eq_dest_test( "sw", 0x2010, 0x10111213 ),
    gen_st_data_eq_dest_test( "sw", 0x2014, 0x14151617 ),

    gen_word_data([
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
    ])

  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    # Test positive offsets

    gen_st_value_test( "sw",   0, 0x00002000, 0xdeadbeef ),
    gen_st_value_test( "sw",   4, 0x00002000, 0x00010203 ),
    gen_st_value_test( "sw",   8, 0x00002000, 0x04050607 ),
    gen_st_value_test( "sw",  12, 0x00002000, 0x08090a0b ),
    gen_st_value_test( "sw",  16, 0x00002000, 0x0c0d0e0f ),
    gen_st_value_test( "sw",  20, 0x00002000, 0xcafecafe ),

    # Test negative offsets

    gen_st_value_test( "sw", -20, 0x00002014, 0xdeadbeef ),
    gen_st_value_test( "sw", -16, 0x00002014, 0x00010203 ),
    gen_st_value_test( "sw", -12, 0x00002014, 0x04050607 ),
    gen_st_value_test( "sw",  -8, 0x00002014, 0x08090a0b ),
    gen_st_value_test( "sw",  -4, 0x00002014, 0x0c0d0e0f ),
    gen_st_value_test( "sw",   0, 0x00002014, 0xcafecafe ),

    # Test positive offset with unaligned base

    gen_st_value_test( "sw",   1, 0x00001fff, 0xdeadbeef ),
    gen_st_value_test( "sw",   5, 0x00001fff, 0x00010203 ),
    gen_st_value_test( "sw",   9, 0x00001fff, 0x04050607 ),
    gen_st_value_test( "sw",  13, 0x00001fff, 0x08090a0b ),
    gen_st_value_test( "sw",  17, 0x00001fff, 0x0c0d0e0f ),
    gen_st_value_test( "sw",  21, 0x00001fff, 0xcafecafe ),

    # Test negative offset with unaligned base

    gen_st_value_test( "sw", -21, 0x00002015, 0xdeadbeef ),
    gen_st_value_test( "sw", -17, 0x00002015, 0x00010203 ),
    gen_st_value_test( "sw", -13, 0x00002015, 0x04050607 ),
    gen_st_value_test( "sw",  -9, 0x00002015, 0x08090a0b ),
    gen_st_value_test( "sw",  -5, 0x00002015, 0x0c0d0e0f ),
    gen_st_value_test( "sw",  -1, 0x00002015, 0xcafecafe ),

    gen_word_data([
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
      0xeeeeeeee,
    ])

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():

  # Generate constant data for data memory

  data = []
  for i in xrange(128):
    data.append( 0xeeeeeeee )

  # Generate random writes to data memory

  asm_code = []
  for i in xrange(100):

    a = random.randint(0,127)
    b = random.randint(0,127)

    base   = Bits( 32, 0x2000 + (4*b) )
    offset = Bits( 16, (4*(a - b)) )
    result = random.randint( 0, 0xffffffff )

    asm_code.append( gen_st_value_test( "sw", offset.int(), base.uint(), result ) )

  # Add the data to the end of the assembly code

  asm_code.append( gen_word_data( data ) )
  return asm_code

