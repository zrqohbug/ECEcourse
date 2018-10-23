#=========================================================================
# mix test case generators
#=========================================================================

import random

from pymtl import *
from inst_utils import *

def gen_mix_inst_random_test( num_insts, num_blocks, num_regs ):

  def gen_mix_inst_random_internal_test():

    seq = range( 1, num_blocks+1 )

    random.shuffle( seq )

    return gen_mix_random_test( num_insts, num_blocks, num_regs, seq )

  return gen_mix_inst_random_internal_test
