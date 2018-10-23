#=========================================================================
# ProcBaseRTL_test.py
#=========================================================================

import pytest
import random

from pymtl   import *
from harness import *
from lab2_proc.ProcBaseRTL import ProcBaseRTL

#-------------------------------------------------------------------------
# lw
#-------------------------------------------------------------------------

import inst_lw

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_lw.gen_basic_test     ) ,
  asm_test( inst_lw.gen_dest_dep_test  ) ,
  asm_test( inst_lw.gen_base_dep_test  ) ,
  asm_test( inst_lw.gen_srcs_dest_test ) ,
  asm_test( inst_lw.gen_value_test     ) ,
  asm_test( inst_lw.gen_random_test    ) ,
])
def test_lw( name, test, dump_vcd ):
  run_test( ProcBaseRTL, test, dump_vcd )

def test_lw_rand_delays( dump_vcd ):
  for i in xrange( 1 ):
    src_delay       = random.randint( 1, 5 )
    sink_delay      = random.randint( 1, 5 )
    mem_stall_prob  = random.uniform(0.0, 0.4)
    mem_latency     = random.randint( 1, 5 )
    run_test( ProcBaseRTL, inst_lw.gen_random_test, dump_vcd, 
              src_delay = src_delay, sink_delay = sink_delay, 
              mem_stall_prob = mem_stall_prob, 
              mem_latency = mem_latency
        )

#-------------------------------------------------------------------------
# sw
#-------------------------------------------------------------------------

import inst_sw

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_sw.gen_basic_test        ),
  asm_test( inst_sw.gen_dest_dep_test     ),
  asm_test( inst_sw.gen_base_dep_test     ),
  asm_test( inst_sw.gen_base_eq_dep_test  ),
  asm_test( inst_sw.gen_data_dep_test     ),
  asm_test( inst_sw.gen_data_eq_dep_test  ),
  asm_test( inst_sw.gen_value_test        ),
  asm_test( inst_sw.gen_random_test       ),
])
def test_sw( name, test, dump_vcd ):
  run_test( ProcBaseRTL, test, dump_vcd )

def test_sw_rand_delays( dump_vcd ):
  for i in xrange( 1 ):
    src_delay       = random.randint( 1, 5 )
    sink_delay      = random.randint( 1, 5 )
    mem_stall_prob  = random.uniform(0.0, 0.4)
    mem_latency     = random.randint( 1, 5 )
    run_test( ProcBaseRTL, inst_sw.gen_random_test, dump_vcd, 
              src_delay = src_delay, sink_delay = sink_delay, 
              mem_stall_prob = mem_stall_prob, 
              mem_latency = mem_latency
        )

