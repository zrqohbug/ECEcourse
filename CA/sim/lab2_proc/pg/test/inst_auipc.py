#=========================================================================
# auipc
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    auipc x1, 0x00010                       # PC=0x200
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw  proc2mngr, x1 > 0x00010200
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
    gen_imm_dest_dep_test( 5, "auipc", 0x000ff, 0x000ff200 ),
    gen_imm_dest_dep_test( 4, "auipc", 0xffff0, 0xffff021c ),
    gen_imm_dest_dep_test( 3, "auipc", 0xfff00, 0xfff00234 ),
    gen_imm_dest_dep_test( 2, "auipc", 0x00fff, 0x00fff248 ),
    gen_imm_dest_dep_test( 1, "auipc", 0xfffff, 0xfffff258 ),
    gen_imm_dest_dep_test( 0, "auipc", 0x0fff0, 0x0fff0264 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [
    gen_imm_value_test( "auipc", 0xff0ff, 0xff0ff200 ),
    gen_imm_value_test( "auipc", 0x0fff0, 0x0fff0208 ),
    gen_imm_value_test( "auipc", 0x00fff, 0x00fff210 ),
    gen_imm_value_test( "auipc", 0xffff0, 0xffff0218 ),
  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  prev = Bits( 32, 0x200 ) - 8
  for i in xrange(100):
    imm  = Bits( 20, random.randint(0,0xfffff) )
    dest = prev + 8 + concat( imm, Bits( 12, 0 ) )
    prev = prev + 8
    asm_code.append( gen_imm_value_test( "auipc", imm.uint(), dest.uint() ) )
  return asm_code
