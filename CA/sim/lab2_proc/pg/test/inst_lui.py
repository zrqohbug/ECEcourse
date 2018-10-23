#=========================================================================
# lui
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    lui x1, 0x0001
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x1 > 0x00001000
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
    gen_imm_dest_dep_test( 5, "lui", 0x000ff, 0x000ff000 ),
    gen_imm_dest_dep_test( 4, "lui", 0xffff0, 0xffff0000 ),
    gen_imm_dest_dep_test( 3, "lui", 0xfff00, 0xfff00000 ),
    gen_imm_dest_dep_test( 2, "lui", 0x00fff, 0x00fff000 ),
    gen_imm_dest_dep_test( 1, "lui", 0xfffff, 0xfffff000 ),
    gen_imm_dest_dep_test( 0, "lui", 0x0fff0, 0x0fff0000 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [
    gen_imm_value_test( "lui", 0xff0ff, 0xff0ff000 ),
    gen_imm_value_test( "lui", 0x0fff0, 0x0fff0000 ),
    gen_imm_value_test( "lui", 0x00fff, 0x00fff000 ),
    gen_imm_value_test( "lui", 0xffff0, 0xffff0000 ),
  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    imm  = Bits( 20, random.randint(0,0xfffff) )
    dest = concat( imm, Bits( 12, 0 ) )
    asm_code.append( gen_imm_value_test( "lui", imm.uint(), dest.uint() ) )
  return asm_code
