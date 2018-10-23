#=========================================================================
# jal
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """

    # Use r3 to track the control flow pattern
    addi  x3, x0, 0     # 0x0200
                        #
    nop                 # 0x0204
    nop                 # 0x0208
    nop                 # 0x020c
    nop                 # 0x0210
    nop                 # 0x0214
    nop                 # 0x0218
    nop                 # 0x021c
    nop                 # 0x0220
                        #
    jal   x1, label_1   # 0x0224
    addi  x3, x3, 0b01  # 0x0228

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

  label_1:
    addi  x3, x3, 0b10

    # Check the link address
    csrw  proc2mngr, x1 > 0x0228 

    # Only the second bit should be set if jump was taken
    csrw  proc2mngr, x3 > 0b10

  """

#-------------------------------------------------------------------------
# gen_value_test with num_nops = 0
#-------------------------------------------------------------------------

def gen_value_0_1_test():
  return [
      gen_jal_value_test( 0, 4, [ 1, 2, 3, 4 ], 0x00001234, 0x0238 ),
  ]
def gen_value_0_2_test():
  return [
      gen_jal_value_test( 0, 4, [ 4, 3, 2, 1 ], 0x00000004, 0x0238 ),
  ]
def gen_value_0_3_test():
  return [
      gen_jal_value_test( 0, 4, [ 1, 3, 2, 4 ], 0x00000134, 0x0238 ),
  ]
def gen_value_0_4_test():
  return [
      gen_jal_value_test( 0, 4, [ 3, 2, 4, 1 ], 0x00003124, 0x0238 ),
  ]
def gen_value_0_5_test():
  return [
      gen_jal_value_test( 0, 4, [ 2, 1, 4, 3 ], 0x00000024, 0x0238 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test with num_nops = 1
#-------------------------------------------------------------------------

def gen_value_1_1_test():
  return [
      gen_jal_value_test( 1, 4, [ 1, 2, 3, 4 ], 0x00001234, 0x024c ),
  ]
def gen_value_1_2_test():
  return [
      gen_jal_value_test( 1, 4, [ 4, 3, 2, 1 ], 0x00000004, 0x024c ),
  ]
def gen_value_1_3_test():
  return [
      gen_jal_value_test( 1, 4, [ 1, 3, 2, 4 ], 0x00000134, 0x024c ),
  ]
def gen_value_1_4_test():
  return [
      gen_jal_value_test( 1, 4, [ 3, 2, 4, 1 ], 0x00003124, 0x024c ),
  ]
def gen_value_1_5_test():
  return [
      gen_jal_value_test( 1, 4, [ 2, 1, 4, 3 ], 0x00000024, 0x024c ),
  ]

#-------------------------------------------------------------------------
# gen_value_test with num_nops = 2
#-------------------------------------------------------------------------

def gen_value_2_1_test():
  return [
      gen_jal_value_test( 2, 4, [ 1, 2, 3, 4 ], 0x00001234, 0x0260 ),
  ]
def gen_value_2_2_test():
  return [
      gen_jal_value_test( 2, 4, [ 4, 3, 2, 1 ], 0x00000004, 0x0260 ),
  ]
def gen_value_2_3_test():
  return [
      gen_jal_value_test( 2, 4, [ 1, 3, 2, 4 ], 0x00000134, 0x0260 ),
  ]
def gen_value_2_4_test():
  return [
      gen_jal_value_test( 2, 4, [ 3, 2, 4, 1 ], 0x00003124, 0x0260 ),
  ]
def gen_value_2_5_test():
  return [
      gen_jal_value_test( 2, 4, [ 2, 1, 4, 3 ], 0x00000024, 0x0260 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test with num_nops = 3
#-------------------------------------------------------------------------

def gen_value_3_1_test():
  return [
      gen_jal_value_test( 3, 4, [ 1, 2, 3, 4 ], 0x00001234, 0x0274 ),
  ]
def gen_value_3_2_test():
  return [
      gen_jal_value_test( 3, 4, [ 4, 3, 2, 1 ], 0x00000004, 0x0274 ),
  ]
def gen_value_3_3_test():
  return [
      gen_jal_value_test( 3, 4, [ 1, 3, 2, 4 ], 0x00000134, 0x0274 ),
  ]
def gen_value_3_4_test():
  return [
      gen_jal_value_test( 3, 4, [ 3, 2, 4, 1 ], 0x00003124, 0x0274 ),
  ]
def gen_value_3_5_test():
  return [
      gen_jal_value_test( 3, 4, [ 2, 1, 4, 3 ], 0x00000024, 0x0274 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test with num_nops = 4
#-------------------------------------------------------------------------

def gen_value_4_1_test():
  return [
      gen_jal_value_test( 4, 4, [ 1, 2, 3, 4 ], 0x00001234, 0x0288 ),
  ]
def gen_value_4_2_test():
  return [
      gen_jal_value_test( 4, 4, [ 4, 3, 2, 1 ], 0x00000004, 0x0288 ),
  ]
def gen_value_4_3_test():
  return [
      gen_jal_value_test( 4, 4, [ 1, 3, 2, 4 ], 0x00000134, 0x0288 ),
  ]
def gen_value_4_4_test():
  return [
      gen_jal_value_test( 4, 4, [ 3, 2, 4, 1 ], 0x00003124, 0x0288 ),
  ]
def gen_value_4_5_test():
  return [
      gen_jal_value_test( 4, 4, [ 2, 1, 4, 3 ], 0x00000024, 0x0288 ),
  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():

  # Generate random writes to data memory

  num_nops = random.randint( 0, 5 )

  num_blocks = 8

  seq = [ 1, 2, 3, 4, 5, 6, 7, 8 ]

  random.shuffle( seq )

  flow_pattern = 0
  
  addr_reg = 0

  idx = 0

  while True:
    flow_pattern = (flow_pattern << 4) + (seq[idx])
    if seq[idx] == num_blocks:
      break
    idx = seq[idx]

  addr_reg = 0x208 + 12 * 8 + (4 * num_nops) * ( 9 )

  return gen_jal_value_test( \
      num_nops = num_nops, num_blocks = num_blocks, \
      seq = seq, flow_pattern = flow_pattern, addr_reg = addr_reg\
  )

