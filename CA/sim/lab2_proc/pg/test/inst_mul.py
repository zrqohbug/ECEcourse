#=========================================================================
# mul
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 5
    csrr x2, mngr2proc < 4
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    mul x3, x1, x2
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 20
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
    gen_rr_dest_dep_test( 5, "mul", 1, 1, 1 ),
    gen_rr_dest_dep_test( 4, "mul", 2, 1, 2 ),
    gen_rr_dest_dep_test( 3, "mul", 3, 1, 3 ),
    gen_rr_dest_dep_test( 2, "mul", 4, 1, 4 ),
    gen_rr_dest_dep_test( 1, "mul", 5, 1, 5 ),
    gen_rr_dest_dep_test( 0, "mul", 6, 1, 6 ),
  ]

#-------------------------------------------------------------------------
# gen_src0_dep_test
#-------------------------------------------------------------------------

def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "mul",  7, 1,  7 ),
    gen_rr_src0_dep_test( 4, "mul",  8, 1,  8 ),
    gen_rr_src0_dep_test( 3, "mul",  9, 1,  9 ),
    gen_rr_src0_dep_test( 2, "mul", 10, 1, 10 ),
    gen_rr_src0_dep_test( 1, "mul", 11, 1, 11 ),
    gen_rr_src0_dep_test( 0, "mul", 12, 1, 12 ),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_test
#-------------------------------------------------------------------------

def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "mul", 1, 13, 13 ),
    gen_rr_src1_dep_test( 4, "mul", 1, 14, 14 ),
    gen_rr_src1_dep_test( 3, "mul", 1, 15, 15 ),
    gen_rr_src1_dep_test( 2, "mul", 1, 16, 16 ),
    gen_rr_src1_dep_test( 1, "mul", 1, 17, 17 ),
    gen_rr_src1_dep_test( 0, "mul", 1, 18, 18 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_test
#-------------------------------------------------------------------------

def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "mul", 12, 2, 24 ),
    gen_rr_srcs_dep_test( 4, "mul", 13, 3, 39 ),
    gen_rr_srcs_dep_test( 3, "mul", 14, 4, 56 ),
    gen_rr_srcs_dep_test( 2, "mul", 15, 5, 75 ),
    gen_rr_srcs_dep_test( 1, "mul", 16, 6, 96 ),
    gen_rr_srcs_dep_test( 0, "mul", 17, 7,119 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "mul", 25, 1, 25 ),
    gen_rr_src1_eq_dest_test( "mul", 26, 1, 26 ),
    gen_rr_src0_eq_src1_test( "mul", 27, 729 ),
    gen_rr_srcs_eq_dest_test( "mul", 28, 784 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_rr_value_test( "mul", 0x00000000, 0x00000000, 0x00000000 ),
    gen_rr_value_test( "mul", 0x00000001, 0x00000001, 0x00000001 ),
    gen_rr_value_test( "mul", 0x00000003, 0x00000007, 0x00000015 ),

    gen_rr_value_test( "mul", 0x00000000, 0xffff8000, 0x00000000 ),
    gen_rr_value_test( "mul", 0x80000000, 0x00000000, 0x00000000 ),
    gen_rr_value_test( "mul", 0x80000000, 0xffff8000, 0x00000000 ), #Overflow

    gen_rr_value_test( "mul", 0x00000000, 0x00007fff, 0x00000000 ),
    gen_rr_value_test( "mul", 0x7fffffff, 0x00000000, 0x00000000 ),
    gen_rr_value_test( "mul", 0x7fffffff, 0x00007fff, 0x7fff8001 ), #Overflow

    gen_rr_value_test( "mul", 0x80000000, 0x00007fff, 0x80000000 ), #Overflow
    gen_rr_value_test( "mul", 0x7fffffff, 0xffff8000, 0x00008000 ), #Overflow

    gen_rr_value_test( "mul", 0x00000000, 0xffffffff, 0x00000000 ),
    gen_rr_value_test( "mul", 0xffffffff, 0x00000001, 0xffffffff ),
    gen_rr_value_test( "mul", 0xffffffff, 0xffffffff, 0x00000001 ), #Overflow

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(0,0xffffffff) )
    src1 = Bits( 32, random.randint(0,0xffffffff) )
    dest = Bits( 32, src0 * src1, trunc = True ) 
    asm_code.append( gen_rr_value_test( "mul", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code

