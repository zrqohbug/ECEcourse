#=========================================================================
# srli
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
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    srli x3, x1, 0x03
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
    gen_rimm_dest_dep_test( 5, "srli", 0x00000f0f, 0x0ff & 0x1f, 0x00000000 ),
    gen_rimm_dest_dep_test( 4, "srli", 0x0000f0f0, 0xff0 & 0x1f, 0x00000000 ),
    gen_rimm_dest_dep_test( 3, "srli", 0x00000f0f, 0xf00 & 0x1f, 0x00000f0f ),
    gen_rimm_dest_dep_test( 2, "srli", 0x0000f0f0, 0x00f & 0x1f, 0x00000001 ),
    gen_rimm_dest_dep_test( 1, "srli", 0x00000f0f, 0xfff & 0x1f, 0x00000000 ),
    gen_rimm_dest_dep_test( 0, "srli", 0x0000f0f0, 0x0f0 & 0x1f, 0x00000000 ),
  ]

#-------------------------------------------------------------------------
# gen_src_dep_test
#-------------------------------------------------------------------------

def gen_src_dep_test():
  return [
    gen_rimm_src_dep_test( 5, "srli", 0x00000f0f, 0x0ff & 0x1f, 0x00000000 ),
    gen_rimm_src_dep_test( 4, "srli", 0x0000f0f0, 0xff0 & 0x1f, 0x00000000 ),
    gen_rimm_src_dep_test( 3, "srli", 0x00000f0f, 0xf00 & 0x1f, 0x00000f0f ),
    gen_rimm_src_dep_test( 2, "srli", 0x0000f0f0, 0xf0f & 0x1f, 0x00000001 ),
    gen_rimm_src_dep_test( 1, "srli", 0x00000f0f, 0xfff & 0x1f, 0x00000000 ),
    gen_rimm_src_dep_test( 0, "srli", 0x0000f0f0, 0x0f0 & 0x1f, 0x00000000 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rimm_src_eq_dest_test( "srli", 0x00000f0f, 0xff0 & 0x1f, 0x00000000 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [
    gen_rimm_value_test( "srli", 0xff00ff00, 0xf0f & 0x1f, 0x0001fe01 ),
    gen_rimm_value_test( "srli", 0x0ff00ff0, 0x0f0 & 0x1f, 0x00000ff0 ),
    gen_rimm_value_test( "srli", 0x00ff00ff, 0x00f & 0x1f, 0x000001fe ),
    gen_rimm_value_test( "srli", 0xf00ff00f, 0xff0 & 0x1f, 0x0000f00f ),
  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src  = Bits( 32, random.randint(0,0xffffffff) )
    imm  = Bits( 12, random.randint(0,0x1f) )
    dest = src >> ( imm & 0x1f )
    asm_code.append( gen_rimm_value_test( "srli", src.uint(), imm.uint(), dest.uint() ) )
  return asm_code

