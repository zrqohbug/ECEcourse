import pytest
import random

from pymtl import *
from harness import *

from lab2_proc.ProcBaseRTL import ProcBaseRTL
from lab2_proc.ProcAltRTL  import ProcAltRTL
from lab2_proc.ProcFL      import ProcFL

import mix
import forward
import branch_jump

@pytest.mark.parametrize( "name,test,num_regs,num_trips", [
  asm_test_param( branch_jump.gen_branch_jump_priority_test, 1, 1  ),
  # Repeat the branch-jump random test 10 times, each with 10 blocks
  asm_test_param( branch_jump.gen_branch_jump_random_test(10), 4, 10 ),
  asm_test_param( forward.gen_store_forward_test, 1, 1  ),
  asm_test_param( forward.gen_forward_priority_test, 1, 1  ),
  # Repeat the forward random test 10 times, each with 10 insts
  asm_test_param( forward.gen_forward_random_test( 10, 3 ), 3, 10  ),
  # Repeat the mix instruction random test 10 times, each with 10 blocks
  asm_test_param( mix.gen_mix_inst_random_test( 8, 10, 3 ), 3, 10  ),
  asm_test_param( mix.gen_mix_inst_random_test( 8, 10, 4 ), 4, 10  ),
  asm_test_param( mix.gen_mix_inst_random_test( 5, 10, 3 ), 3, 10  ),
])
def test_extra( name, test, num_regs, num_trips, dump_vcd ):

  for _ in xrange( num_trips ):

    src_delay       = random.randint( 0, 5 )
    sink_delay      = random.randint( 0, 5 )
    mem_stall_prob  = random.uniform( 0.0, 0.4 )
    mem_latency     = random.randint( 0, 5 )

    test_case = test()

    print 'src_delay={}, sink_delay={}, mem_stall_prob={}, \
 mem_latency={}'.format( src_delay, sink_delay, mem_stall_prob,\
    mem_latency )

    ref_output = []

    # First generate the reference output

    run_test( ProcFL, lambda : test_case, None, 
              src_delay = src_delay, sink_delay = sink_delay, 
              mem_stall_prob = mem_stall_prob, 
              mem_latency = mem_latency, print_trace = True, 
              ref_output = ref_output, num_regs = num_regs
        )

    # Then generate the complete test program ( includes 
    # reference output )

    test_case = test_case.split('\n')[:-num_regs]

    for i in xrange( num_regs ):

      test_case.append( '    csrw  proc2mngr, x{idx} > 0x{result:x}'.format(\
              idx = i+1, result = ref_output[ i ].uint()
          ) )

    test_case = '\n'.join( test_case )

    # Feed the test case to both baseline and alt

    run_test( ProcBaseRTL, lambda : test_case, dump_vcd, 
              src_delay = src_delay, sink_delay = sink_delay, 
              mem_stall_prob = mem_stall_prob, 
              mem_latency = mem_latency, print_trace = True, 
        )

    run_test( ProcAltRTL, lambda : test_case, dump_vcd, 
              src_delay = src_delay, sink_delay = sink_delay, 
              mem_stall_prob = mem_stall_prob, 
              mem_latency = mem_latency, print_trace = True, 
        )

# if __name__ == '__main__':
  # test_extra( 'branch_jump', branch_jump.gen_branch_jump_random_test(10),
      # 4, 10, '')
