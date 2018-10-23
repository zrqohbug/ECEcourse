#=========================================================================
# forwarding test case generators
#=========================================================================

import random

from pymtl import *
from inst_utils import *

def gen_store_forward_test():
  return """\
    addi  x2, x0, 0x10
    addi  x3, x0, 0x100

    sw    x2, 0(x03)
    lw    x1, 0(x03)

    csrw  proc2mngr, x1 > 0x10"""

def gen_forward_priority_test():
  return """\
    addi  x1, x0, 0x0
    addi  x1, x1, 0x1
    addi  x1, x1, 0x2
    addi  x1, x1, 0x4
    addi  x1, x1, 0x8
    addi  x1, x1, 0x10
    addi  x1, x1, 0x20
    csrw  proc2mngr, x1 > 0x3f"""

def gen_forward_random_test( num_insts, num_regs ):

  def gen_forward_random_internal_test():

    test_case =  ''

    for i in xrange( num_regs ):

      test_case += '    addi  x{}, x0, 8\n'.format( i+1 )

    for i in xrange( num_insts ):

      flag = random.randint( 1, 3 )

      if flag == 1:
        inst = '    add   x{}, x{}, x{}\n'.format(\
              random.randint( 1, num_regs ), 
              random.randint( 1, num_regs ), 
              random.randint( 1, num_regs ), 
            )
      elif flag == 2:
        inst = '    mul   x{}, x{}, x{}\n'.format(\
              random.randint( 1, num_regs ), 
              random.randint( 1, num_regs ), 
              random.randint( 1, num_regs ), 
            )
      else:
        inst = '    auipc   x{}, 0\n'.format(\
              random.randint( 1, num_regs ), 
            )

      test_case += inst

    for i in xrange( num_regs ):

      test_case += '    csrw  proc2mngr, x{} > 0x0'.format(\
              i+1
          )
      if i != num_regs - 1:
        test_case += '\n'

    return test_case

  return gen_forward_random_internal_test
