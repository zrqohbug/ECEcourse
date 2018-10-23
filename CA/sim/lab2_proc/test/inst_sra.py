#=========================================================================
# sra
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 0x00008000
    csrr x2, mngr2proc < 0x00000003
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sra x3, x1, x2
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x00001000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------

def gen_dest_dep_test():
  return [
    gen_rr_dest_dep_test( 5, "sra", 1, 1, 0 ),
    gen_rr_dest_dep_test( 4, "sra", 2, 1, 1 ),
    gen_rr_dest_dep_test( 3, "sra", 3, 1, 1 ),
    gen_rr_dest_dep_test( 2, "sra", 4, 1, 2 ),
    gen_rr_dest_dep_test( 1, "sra", 5, 1, 2 ),
    gen_rr_dest_dep_test( 0, "sra", 6, 1, 3 ),
  ]

#-------------------------------------------------------------------------
# gen_src0_dep_test
#-------------------------------------------------------------------------

def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "sra",  7, 1,  3 ),
    gen_rr_src0_dep_test( 4, "sra",  8, 1,  4 ),
    gen_rr_src0_dep_test( 3, "sra",  9, 1,  4 ),
    gen_rr_src0_dep_test( 2, "sra", 10, 1,  5 ),
    gen_rr_src0_dep_test( 1, "sra", 11, 1,  5 ),
    gen_rr_src0_dep_test( 0, "sra", 12, 1,  6 ),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_test
#-------------------------------------------------------------------------

def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "sra", 1, 13, 0 ),
    gen_rr_src1_dep_test( 4, "sra", 1, 14, 0 ),
    gen_rr_src1_dep_test( 3, "sra", 1, 15, 0 ),
    gen_rr_src1_dep_test( 2, "sra", 1, 16, 0 ),
    gen_rr_src1_dep_test( 1, "sra", 1, 17, 0 ),
    gen_rr_src1_dep_test( 0, "sra", 1, 18, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_test
#-------------------------------------------------------------------------

def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "sra", 12, 2, 3 ),
    gen_rr_srcs_dep_test( 4, "sra", 13, 3, 1 ),
    gen_rr_srcs_dep_test( 3, "sra", 14, 4, 0 ),
    gen_rr_srcs_dep_test( 2, "sra", 15, 5, 0 ),
    gen_rr_srcs_dep_test( 1, "sra", 16, 6, 0 ),
    gen_rr_srcs_dep_test( 0, "sra", 17, 7, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "sra", 25, 1, 12 ),
    gen_rr_src1_eq_dest_test( "sra", 26, 1, 13 ),
    gen_rr_src0_eq_src1_test( "sra", 27, 0 ),
    gen_rr_srcs_eq_dest_test( "sra", 28, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_rr_value_test( "sra", 0x00000000, 0x00000000, 0x00000000 ),
    gen_rr_value_test( "sra", 0x00000001, 0x00000001, 0x00000000 ),
    gen_rr_value_test( "sra", 0x00000003, 0x00000007, 0x00000000 ),

    gen_rr_value_test( "sra", 0x00000000, 0xffff8000, 0x00000000 ),
    gen_rr_value_test( "sra", 0x80000000, 0x00000000, 0x80000000 ),
    gen_rr_value_test( "sra", 0x80000000, 0xffff8000, 0x80000000 ),

    gen_rr_value_test( "sra", 0x00000000, 0x00007fff, 0x00000000 ),
    gen_rr_value_test( "sra", 0x7fffffff, 0x00000000, 0x7fffffff ),
    gen_rr_value_test( "sra", 0x7fffffff, 0x00007fff, 0x00000000 ),

    gen_rr_value_test( "sra", 0x80000000, 0x00007fff, 0xffffffff ),
    gen_rr_value_test( "sra", 0x7fffffff, 0xffff8000, 0x7fffffff ),

    gen_rr_value_test( "sra", 0x00000000, 0xffffffff, 0x00000000 ),
    gen_rr_value_test( "sra", 0xffffffff, 0x00000001, 0xffffffff ),
    gen_rr_value_test( "sra", 0xffffffff, 0xffffffff, 0xffffffff ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(0,0xffffffff) )
    src1 = Bits( 32, random.randint(0,0xffffffff) )
    dest = ( sext( src0, 64 ) >> ( src1 & 0x1f ) )[ 0:32 ]
    asm_code.append( gen_rr_value_test( "sra", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code

