#=========================================================================
# IntMulFL_test
#=========================================================================

import pytest
import random

random.seed(0xdeadbeef)

from pymtl      import *
from pclib.test import mk_test_case_table, run_sim
from pclib.test import TestSource, TestSink

from lab1_imul.IntMulFL   import IntMulFL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( s, imul, src_msgs, sink_msgs,
                src_delay, sink_delay,
                dump_vcd=False, test_verilog=False ):

    # Instantiate models

    s.src  = TestSource ( Bits(64), src_msgs,  src_delay  )
    s.imul = imul
    s.sink = TestSink   ( Bits(32), sink_msgs, sink_delay )

    # Dump VCD

    if dump_vcd:
      s.imul.vcd_file = dump_vcd

    #Translation

    if test_verilog:
      s.imul = TranslationTool( s.imul )

    # Connect

    s.connect( s.src.out,  s.imul.req  )
    s.connect( s.imul.resp, s.sink.in_ )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace()  + " > " + \
           s.imul.line_trace()  + " > " + \
           s.sink.line_trace()

#-------------------------------------------------------------------------
# mk_req_msg
#-------------------------------------------------------------------------

def req( a, b ):
  msg = Bits( 64 )
  msg[32:64] = Bits( 32, a, trunc=True )
  msg[ 0:32] = Bits( 32, b, trunc=True )
  return msg

def resp( a ):
  return Bits( 32, a, trunc=True )

#----------------------------------------------------------------------
# Test Case: small positive * positive
#----------------------------------------------------------------------

small_pos_pos_msgs = [
  req(  2,  3 ), resp(   6 ),
  req(  4,  5 ), resp(  20 ),
  req(  3,  4 ), resp(  12 ),
  req( 10, 13 ), resp( 130 ),
  req(  8,  7 ), resp(  56 ),
]

#----------------------------------------------------------------------
# Test Case: small positive * negative
#----------------------------------------------------------------------

small_pos_neg_msgs = [
  req(  1,  -4 ), resp(   -4 ),
  req(  2,  -7 ), resp(  -14 ),
  req(  4,  -6 ), resp(  -24 ),
  req(  5,  -1 ), resp(   -5 ),
  req( 18, -16 ), resp( -288 ),
]

#----------------------------------------------------------------------
# Test Case: small negative * positive
#----------------------------------------------------------------------
small_neg_pos_msgs = [
  req( -1,   3 ), resp(   -3 ),
  req( -2,  10 ), resp(  -20 ),
  req( -8,   9 ), resp(  -72 ),
  req(-11,  12 ), resp( -132 ),
  req( -7,  16 ), resp( -112 ),
]

#----------------------------------------------------------------------
# Test Case: small negative * negative
#----------------------------------------------------------------------

small_neg_neg_msgs = [
  req(  -1, -10), resp(  10 ),
  req(  -2,  -8), resp(  16 ),
  req(  -4,  -7), resp(  28 ),
  req(  -7,  -5), resp(  35 ),
  req( -11, -17), resp( 187 ),
]

#----------------------------------------------------------------------
# Test Case: large positive * positive
#----------------------------------------------------------------------

large_pos_pos_msgs = [
  req( 2147483647, 2147483647) , resp(          1 ),
  req(      25741,      58741) , resp( 1512052081 ),
  req(      36524,     117428) , resp(   -6027024 ),
  req( 1073741824, 2147483647) , resp(-1073741824 ),
]

#----------------------------------------------------------------------
# Test Case: large positive * negative
#----------------------------------------------------------------------

large_pos_neg_msgs = [
  req( 2147483647,-2147483648) , resp(-2147483648 ),
  req( 1073741824,-2147483648) , resp(          0 ),
  req(      12845,     -45874) , resp( -589251530 ),
  req(      25874,    -147854) , resp(  469392900 ),
]

#----------------------------------------------------------------------
# Test Case: large negative * positive
#----------------------------------------------------------------------

large_neg_pos_msgs = [
  req(-2147483648, 2147483647) , resp(-2147483648 ),
  req(-2147483647, 2147483647) , resp(         -1 ),
  req(     -24875,      57439) , resp(-1428795125 ),
  req(     -58471,     142587) , resp(  252730115 ),
]

#----------------------------------------------------------------------
# Test Case: large negative * negative
#----------------------------------------------------------------------

large_neg_neg_msgs = [
  req(-2147483648,-2147483648) , resp(          0 ),
  req(-2147483647,-2147483648) , resp(-2147483648 ),
  req(     -12486,     -65879) , resp(  822565194 ),
  req(     -54789,    -154897) , resp( -103282859 ),
]

#----------------------------------------------------------------------
# Test Case:  multiply with zero
#----------------------------------------------------------------------

zero_mul_msgs = [
  req(          0, 2147483647) , resp(          0 ),
  req(          0,-2147483648) , resp(          0 ),
  req(          0,          0) , resp(          0 ),
  req( 2147483647,          0) , resp(          0 ),
  req(-2147483648,          0) , resp(          0 ),
]

#----------------------------------------------------------------------
# Test Case: multiply with low-bits masked off number
#----------------------------------------------------------------------

low_mask_msgs = [
  req(     21536 ,        241) , resp(    5190176 ),
  req(       640 ,        -85) , resp(     -54400 ),
  req(      -224 ,       1125) , resp(    -252000 ),
  req(       -64 ,       -258) , resp(      16512 ),
]

#----------------------------------------------------------------------
# Test Case: multiply with middle-bits masked off number
#----------------------------------------------------------------------

mid_mask_msgs = [
  req(       271 ,      14852) , resp(    4024892 ),
  req(      4710 ,      -8547) , resp(  -40256370 ),
  req(    -65365 ,      74528) , resp( -576555424 ),
  req(   -130597 ,     -12487) , resp( 1630764739 ),
]

#----------------------------------------------------------------------
# Test Case: multiply with sparse number with many zeros
#----------------------------------------------------------------------
sparse_num_msgs = [
  req(       273 ,      14589) , resp(    3982797 ),
  req(-2147483390,       7458) , resp(    1924164 ),
]

#----------------------------------------------------------------------
# Test Case: multiply with dense number with few zeros
#----------------------------------------------------------------------

dense_num_msgs = [
  req( 2147483643,      -1485) , resp(-2147476223 ),
  req(        -33,     -58795) , resp(    1940235 ),
]

#----------------------------------------------------------------------
# Test Case: random test and random sink and src delay
#----------------------------------------------------------------------
random_msgs = []
for i in xrange(40):
  a = random.randint(0,0xffffffff)
  b = random.randint(0,0xffffffff)
  c = a * b
  random_msgs.extend([ req( a, b ), resp(c) ])

src_delay = random.randint(0,7)
sink_delay = random.randint(0,7)


#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                      "msgs                 src_delay sink_delay"),
  [ "small_pos_pos",     small_pos_pos_msgs,   0,        0          ],
  [ "small_pos_neg",     small_pos_neg_msgs,   0,        0          ],
  [ "small_neg_pos",     small_neg_pos_msgs,   0,        0          ],
  [ "small_neg_neg",     small_neg_neg_msgs,   0,        0          ],
  [ "large_pos_pos",     large_pos_pos_msgs,   0,        0          ],
  [ "large_pos_neg",     large_pos_neg_msgs,   0,        0          ],
  [ "large_neg_pos",     large_neg_pos_msgs,   0,        0          ],
  [ "large_neg_neg",     large_neg_neg_msgs,   0,        0          ],
  [ "zero_mul",          zero_mul_msgs,        0,        0          ],
  [ "low_bit_masked",    low_mask_msgs,        0,        0          ],
  [ "mid_bit_masked",    mid_mask_msgs,        0,        0          ],
  [ "sparse_num_mul",    sparse_num_msgs,      0,        0          ],
  [ "dense_num_mul",     dense_num_msgs,       0,        0          ],
  [ "random_mul",        random_msgs,          0,        0          ],
  [ "random_mul_delay",  random_msgs,          src_delay,sink_delay ],
])
#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd ):
  run_sim( TestHarness( IntMulFL(),
                        test_params.msgs[::2], test_params.msgs[1::2],
                        test_params.src_delay, test_params.sink_delay ),
           dump_vcd )

