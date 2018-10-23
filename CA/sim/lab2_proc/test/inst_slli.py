#=========================================================================
# slli
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 0x80008000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slli x3, x1, 0x03
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x00040000
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
    gen_rimm_dest_dep_test( 5, "slli", 0x00000f0f, 0x0ff & 0x1f, 0x80000000 ),
    gen_rimm_dest_dep_test( 4, "slli", 0x0000f0f0, 0xff0 & 0x1f, 0xf0f00000 ),
    gen_rimm_dest_dep_test( 3, "slli", 0x00000f0f, 0xf00 & 0x1f, 0x00000f0f ),
    gen_rimm_dest_dep_test( 2, "slli", 0x0000f0f0, 0x00f & 0x1f, 0x78780000 ),
    gen_rimm_dest_dep_test( 1, "slli", 0x00000f0f, 0xfff & 0x1f, 0x80000000 ),
    gen_rimm_dest_dep_test( 0, "slli", 0x0000f0f0, 0x0f0 & 0x1f, 0xf0f00000 ),
  ]

#-------------------------------------------------------------------------
# gen_src_dep_test
#-------------------------------------------------------------------------

def gen_src_dep_test():
  return [
    gen_rimm_src_dep_test( 5, "slli", 0x00000f0f, 0x0ff & 0x1f, 0x80000000 ),
    gen_rimm_src_dep_test( 4, "slli", 0x0000f0f0, 0xff0 & 0x1f, 0xf0f00000 ),
    gen_rimm_src_dep_test( 3, "slli", 0x00000f0f, 0xf00 & 0x1f, 0x00000f0f ),
    gen_rimm_src_dep_test( 2, "slli", 0x0000f0f0, 0xf0f & 0x1f, 0x78780000 ),
    gen_rimm_src_dep_test( 1, "slli", 0x00000f0f, 0xfff & 0x1f, 0x80000000 ),
    gen_rimm_src_dep_test( 0, "slli", 0x0000f0f0, 0x0f0 & 0x1f, 0xf0f00000 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rimm_src_eq_dest_test( "slli", 0x00000f0f, 0xff0 & 0x1f, 0x0f0f0000 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [
    gen_rimm_value_test( "slli", 0xff00ff00, 0xf0f & 0x1f, 0x7f800000 ),
    gen_rimm_value_test( "slli", 0x0ff00ff0, 0x0f0 & 0x1f, 0x0ff00000 ),
    gen_rimm_value_test( "slli", 0x00ff00ff, 0x00f & 0x1f, 0x807f8000 ),
    gen_rimm_value_test( "slli", 0xf00ff00f, 0xff0 & 0x1f, 0xf00f0000 ),
  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src  = Bits( 32, random.randint(0,0xffffffff) )
    imm  = Bits( 12, random.randint(0,0x1f) )
    dest = Bits( 32, src << sext(imm,32), trunc = True )
    asm_code.append( gen_rimm_value_test( "slli", src.uint(), imm.uint(), dest.uint() ) )
  return asm_code

