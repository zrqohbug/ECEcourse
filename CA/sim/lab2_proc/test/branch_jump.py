#=========================================================================
# branch and jump test case generators
#=========================================================================

import random

from pymtl import *
from inst_utils import *

def gen_branch_jump_priority_test():
  return """\
    # Use x1 to track the control flow pattern
    addi  x1, x0, 0

    beq   x1, x0, label_1
    jal   x0, label_2

  label_1:
    addi  x1, x1, 0x1
    lui   x2, %hi[label_3]
    addi  x2, x2, %lo[label_3]
    jalr  x0, x2, 0
    jal   x0, label_1

  label_2:
    addi  x1, x1, 0x2
    jal   x0, label_4

  label_3:
    beq   x0, x0, label_2
    addi  x1, x1, 0x4
    jal   x0, label_4

  label_4:
    csrw  proc2mngr, x1 > 0x0010"""

def gen_branch_jump_random_test( num_blocks ):

  def gen_branch_jump_random_internal_test():

    seq = range( 1, num_blocks+1 )

    random.shuffle( seq )

    return gen_beq_jal_jalr_random_test( num_blocks, seq )

  return gen_branch_jump_random_internal_test
