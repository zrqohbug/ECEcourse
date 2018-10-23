#=========================================================================
# ProcBaseRTL_test.py
#=========================================================================

import pytest
import random

from pymtl   import *
from harness import *
from lab2_proc.ProcBaseRTL import ProcBaseRTL

#-------------------------------------------------------------------------
# jal
#-------------------------------------------------------------------------

import inst_jal

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_jal.gen_basic_test      ) ,
  asm_test( inst_jal.gen_value_0_1_test  ) ,
  asm_test( inst_jal.gen_value_0_2_test  ) ,
  asm_test( inst_jal.gen_value_0_3_test  ) ,
  asm_test( inst_jal.gen_value_0_4_test  ) ,
  asm_test( inst_jal.gen_value_0_5_test  ) ,
  asm_test( inst_jal.gen_value_1_1_test  ) ,
  asm_test( inst_jal.gen_value_1_2_test  ) ,
  asm_test( inst_jal.gen_value_1_3_test  ) ,
  asm_test( inst_jal.gen_value_1_4_test  ) ,
  asm_test( inst_jal.gen_value_1_5_test  ) ,
  asm_test( inst_jal.gen_value_2_1_test  ) ,
  asm_test( inst_jal.gen_value_2_2_test  ) ,
  asm_test( inst_jal.gen_value_2_3_test  ) ,
  asm_test( inst_jal.gen_value_2_4_test  ) ,
  asm_test( inst_jal.gen_value_2_5_test  ) ,
  asm_test( inst_jal.gen_value_3_1_test  ) ,
  asm_test( inst_jal.gen_value_3_2_test  ) ,
  asm_test( inst_jal.gen_value_3_3_test  ) ,
  asm_test( inst_jal.gen_value_3_4_test  ) ,
  asm_test( inst_jal.gen_value_3_5_test  ) ,
  asm_test( inst_jal.gen_value_4_1_test  ) ,
  asm_test( inst_jal.gen_value_4_2_test  ) ,
  asm_test( inst_jal.gen_value_4_3_test  ) ,
  asm_test( inst_jal.gen_value_4_4_test  ) ,
  asm_test( inst_jal.gen_value_4_5_test  ) ,
  asm_test( inst_jal.gen_random_test ) ,
])
def test_jal( name, test, dump_vcd ):
  run_test( ProcBaseRTL, test, dump_vcd )

def test_jal_rand_delays( dump_vcd ):
  for i in xrange( 10 ):
    src_delay       = random.randint( 1, 5 )
    sink_delay      = random.randint( 1, 5 )
    mem_stall_prob  = random.uniform(0.0, 0.4)
    mem_latency     = random.randint( 1, 5 )
    run_test( ProcBaseRTL, inst_jal.gen_random_test, dump_vcd, 
              src_delay = src_delay, sink_delay = sink_delay, 
              mem_stall_prob = mem_stall_prob, 
              mem_latency = mem_latency
        )

#-------------------------------------------------------------------------
# jalr
#-------------------------------------------------------------------------

import inst_jalr

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_jalr.gen_basic_test  ) ,
  asm_test( inst_jalr.gen_value_0_1_test  ) ,
  asm_test( inst_jalr.gen_value_0_2_test  ) ,
  asm_test( inst_jalr.gen_value_0_3_test  ) ,
  asm_test( inst_jalr.gen_value_0_4_test  ) ,
  asm_test( inst_jalr.gen_value_0_5_test  ) ,
  asm_test( inst_jalr.gen_value_1_1_test  ) ,
  asm_test( inst_jalr.gen_value_1_2_test  ) ,
  asm_test( inst_jalr.gen_value_1_3_test  ) ,
  asm_test( inst_jalr.gen_value_1_4_test  ) ,
  asm_test( inst_jalr.gen_value_1_5_test  ) ,
  asm_test( inst_jalr.gen_value_2_1_test  ) ,
  asm_test( inst_jalr.gen_value_2_2_test  ) ,
  asm_test( inst_jalr.gen_value_2_3_test  ) ,
  asm_test( inst_jalr.gen_value_2_4_test  ) ,
  asm_test( inst_jalr.gen_value_2_5_test  ) ,
  asm_test( inst_jalr.gen_value_3_1_test  ) ,
  asm_test( inst_jalr.gen_value_3_2_test  ) ,
  asm_test( inst_jalr.gen_value_3_3_test  ) ,
  asm_test( inst_jalr.gen_value_3_4_test  ) ,
  asm_test( inst_jalr.gen_value_3_5_test  ) ,
  asm_test( inst_jalr.gen_value_4_1_test  ) ,
  asm_test( inst_jalr.gen_value_4_2_test  ) ,
  asm_test( inst_jalr.gen_value_4_3_test  ) ,
  asm_test( inst_jalr.gen_value_4_4_test  ) ,
  asm_test( inst_jalr.gen_value_4_5_test  ) ,
  asm_test( inst_jalr.gen_random_test ) ,
])
def test_jalr( name, test, dump_vcd ):
  run_test( ProcBaseRTL, test, dump_vcd )

def test_jalr_rand_delays( dump_vcd ):
  for i in xrange( 10 ):
    src_delay       = random.randint( 1, 5 )
    sink_delay      = random.randint( 1, 5 )
    mem_stall_prob  = random.uniform(0.0, 0.4)
    mem_latency     = random.randint( 1, 5 )
    run_test( ProcBaseRTL, inst_jalr.gen_random_test, dump_vcd, 
              src_delay = src_delay, sink_delay = sink_delay, 
              mem_stall_prob = mem_stall_prob, 
              mem_latency = mem_latency
        )

