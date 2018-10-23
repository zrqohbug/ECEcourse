#=========================================================================
# ProcBaseRTL_alu_test.py
#=========================================================================

import pytest
import random

from pymtl   import *
from harness import *
from lab2_proc.ProcBaseRTL import ProcBaseRTL

#-------------------------------------------------------------------------
# add
#-------------------------------------------------------------------------

import inst_add

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_add.gen_basic_test     ) ,
  asm_test( inst_add.gen_dest_dep_test  ) ,
  asm_test( inst_add.gen_src0_dep_test  ) ,
  asm_test( inst_add.gen_src1_dep_test  ) ,
  asm_test( inst_add.gen_srcs_dep_test  ) ,
  asm_test( inst_add.gen_srcs_dest_test ) ,
  asm_test( inst_add.gen_value_test     ) ,
  asm_test( inst_add.gen_random_test    ) ,
])
def test_add( name, test, dump_vcd ):
  run_test( ProcBaseRTL, test, dump_vcd )

def test_add_rand_delays( dump_vcd ):
  for i in xrange( 1 ):
    src_delay       = random.randint( 1, 5 )
    sink_delay      = random.randint( 1, 5 )
    mem_stall_prob  = random.uniform(0.0, 0.4)
    mem_latency     = random.randint( 1, 5 )
    run_test( ProcBaseRTL, inst_add.gen_random_test, dump_vcd, 
              src_delay = src_delay, sink_delay = sink_delay, 
              mem_stall_prob = mem_stall_prob, 
              mem_latency = mem_latency
        )

#-------------------------------------------------------------------------
# sub
#-------------------------------------------------------------------------

import inst_sub

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_sub.gen_basic_test     ) ,
  asm_test( inst_sub.gen_dest_dep_test  ) ,
  asm_test( inst_sub.gen_src0_dep_test  ) ,
  asm_test( inst_sub.gen_src1_dep_test  ) ,
  asm_test( inst_sub.gen_srcs_dep_test  ) ,
  asm_test( inst_sub.gen_srcs_dest_test ) ,
  asm_test( inst_sub.gen_value_test     ) ,
  asm_test( inst_sub.gen_random_test    ) ,
])
def test_sub( name, test, dump_vcd ):
  run_test( ProcBaseRTL, test, dump_vcd )

def test_sub_rand_delays( dump_vcd ):
  for i in xrange( 1 ):
    src_delay       = random.randint( 1, 5 )
    sink_delay      = random.randint( 1, 5 )
    mem_stall_prob  = random.uniform(0.0, 0.4)
    mem_latency     = random.randint( 1, 5 )
    run_test( ProcBaseRTL, inst_sub.gen_random_test, dump_vcd, 
              src_delay = src_delay, sink_delay = sink_delay, 
              mem_stall_prob = mem_stall_prob, 
              mem_latency = mem_latency
            )

#-------------------------------------------------------------------------
# mul
#-------------------------------------------------------------------------

import inst_mul

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_mul.gen_basic_test     ) ,
  asm_test( inst_mul.gen_dest_dep_test  ) ,
  asm_test( inst_mul.gen_src0_dep_test  ) ,
  asm_test( inst_mul.gen_src1_dep_test  ) ,
  asm_test( inst_mul.gen_srcs_dep_test  ) ,
  asm_test( inst_mul.gen_srcs_dest_test ) ,
  asm_test( inst_mul.gen_value_test     ) ,
  asm_test( inst_mul.gen_random_test    ) ,
])
def test_mul( name, test, dump_vcd ):
  run_test( ProcBaseRTL, test, dump_vcd )

def test_mul_rand_delays( dump_vcd ):
  for i in xrange( 1 ):
    src_delay       = random.randint( 1, 5 )
    sink_delay      = random.randint( 1, 5 )
    mem_stall_prob  = random.uniform(0.0, 0.4)
    mem_latency     = random.randint( 1, 5 )
    run_test( ProcBaseRTL, inst_mul.gen_random_test, dump_vcd, 
              src_delay = src_delay, sink_delay = sink_delay, 
              mem_stall_prob = mem_stall_prob, 
              mem_latency = mem_latency
            )

#-------------------------------------------------------------------------
# and
#-------------------------------------------------------------------------

import inst_and

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_and.gen_basic_test     ) ,
  asm_test( inst_and.gen_dest_dep_test  ) ,
  asm_test( inst_and.gen_src0_dep_test  ) ,
  asm_test( inst_and.gen_src1_dep_test  ) ,
  asm_test( inst_and.gen_srcs_dep_test  ) ,
  asm_test( inst_and.gen_srcs_dest_test ) ,
  asm_test( inst_and.gen_value_test     ) ,
  asm_test( inst_and.gen_random_test    ) ,
])
def test_and( name, test, dump_vcd ):
  run_test( ProcBaseRTL, test, dump_vcd )

def test_and_rand_delays( dump_vcd ):
  for i in xrange( 1 ):
    src_delay       = random.randint( 1, 5 )
    sink_delay      = random.randint( 1, 5 )
    mem_stall_prob  = random.uniform(0.0, 0.4)
    mem_latency     = random.randint( 1, 5 )
    run_test( ProcBaseRTL, inst_and.gen_random_test, dump_vcd,
              src_delay = src_delay, sink_delay = sink_delay, 
              mem_stall_prob = mem_stall_prob, 
              mem_latency = mem_latency
            )

#-------------------------------------------------------------------------
# or
#-------------------------------------------------------------------------

import inst_or

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_or.gen_basic_test     ) ,
  asm_test( inst_or.gen_dest_dep_test  ) ,
  asm_test( inst_or.gen_src0_dep_test  ) ,
  asm_test( inst_or.gen_src1_dep_test  ) ,
  asm_test( inst_or.gen_srcs_dep_test  ) ,
  asm_test( inst_or.gen_srcs_dest_test ) ,
  asm_test( inst_or.gen_value_test     ) ,
  asm_test( inst_or.gen_random_test    ) ,
])
def test_or( name, test, dump_vcd ):
  run_test( ProcBaseRTL, test, dump_vcd )

def test_or_rand_delays( dump_vcd ):
  for i in xrange( 1 ):
    src_delay       = random.randint( 1, 5 )
    sink_delay      = random.randint( 1, 5 )
    mem_stall_prob  = random.uniform(0.0, 0.4)
    mem_latency     = random.randint( 1, 5 )
    run_test( ProcBaseRTL, inst_or.gen_random_test, dump_vcd, 
              src_delay = src_delay, sink_delay = sink_delay, 
              mem_stall_prob = mem_stall_prob, 
              mem_latency = mem_latency
            )

#-------------------------------------------------------------------------
# xor
#-------------------------------------------------------------------------

import inst_xor

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_xor.gen_basic_test     ) ,
  asm_test( inst_xor.gen_dest_dep_test  ) ,
  asm_test( inst_xor.gen_src0_dep_test  ) ,
  asm_test( inst_xor.gen_src1_dep_test  ) ,
  asm_test( inst_xor.gen_srcs_dep_test  ) ,
  asm_test( inst_xor.gen_srcs_dest_test ) ,
  asm_test( inst_xor.gen_value_test     ) ,
  asm_test( inst_xor.gen_random_test    ) ,
])
def test_xor( name, test, dump_vcd ):
  run_test( ProcBaseRTL, test, dump_vcd )

def test_xor_rand_delays( dump_vcd ):
  for i in xrange( 1 ):
    src_delay       = random.randint( 1, 5 )
    sink_delay      = random.randint( 1, 5 )
    mem_stall_prob  = random.uniform(0.0, 0.4)
    mem_latency     = random.randint( 1, 5 )
    run_test( ProcBaseRTL, inst_xor.gen_random_test, dump_vcd, 
              src_delay = src_delay, sink_delay = sink_delay, 
              mem_stall_prob = mem_stall_prob, 
              mem_latency = mem_latency
            )

#-------------------------------------------------------------------------
# slt
#-------------------------------------------------------------------------

import inst_slt

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_slt.gen_basic_test     ) ,
  asm_test( inst_slt.gen_dest_dep_test  ) ,
  asm_test( inst_slt.gen_src0_dep_test  ) ,
  asm_test( inst_slt.gen_src1_dep_test  ) ,
  asm_test( inst_slt.gen_srcs_dep_test  ) ,
  asm_test( inst_slt.gen_srcs_dest_test ) ,
  asm_test( inst_slt.gen_value_test     ) ,
  asm_test( inst_slt.gen_random_test    ) ,
])
def test_slt( name, test, dump_vcd ):
  run_test( ProcBaseRTL, test, dump_vcd )

def test_slt_rand_delays( dump_vcd ):
  for i in xrange( 1 ):
    src_delay       = random.randint( 1, 5 )
    sink_delay      = random.randint( 1, 5 )
    mem_stall_prob  = random.uniform(0.0, 0.4)
    mem_latency     = random.randint( 1, 5 )
    run_test( ProcBaseRTL, inst_slt.gen_random_test, dump_vcd,
              src_delay = src_delay, sink_delay = sink_delay, 
              mem_stall_prob = mem_stall_prob, 
              mem_latency = mem_latency
            )

#-------------------------------------------------------------------------
# sltu
#-------------------------------------------------------------------------

import inst_sltu

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_sltu.gen_basic_test     ) ,
  asm_test( inst_sltu.gen_dest_dep_test  ) ,
  asm_test( inst_sltu.gen_src0_dep_test  ) ,
  asm_test( inst_sltu.gen_src1_dep_test  ) ,
  asm_test( inst_sltu.gen_srcs_dep_test  ) ,
  asm_test( inst_sltu.gen_srcs_dest_test ) ,
  asm_test( inst_sltu.gen_value_test     ) ,
  asm_test( inst_sltu.gen_random_test    ) ,
])
def test_sltu( name, test, dump_vcd ):
  run_test( ProcBaseRTL, test, dump_vcd )

def test_sltu_rand_delays( dump_vcd ):
  for i in xrange( 1 ):
    src_delay       = random.randint( 1, 5 )
    sink_delay      = random.randint( 1, 5 )
    mem_stall_prob  = random.uniform(0.0, 0.4)
    mem_latency     = random.randint( 1, 5 )
    run_test( ProcBaseRTL, inst_sltu.gen_random_test, dump_vcd, 
              src_delay = src_delay, sink_delay = sink_delay, 
              mem_stall_prob = mem_stall_prob, 
              mem_latency = mem_latency
            )

#-------------------------------------------------------------------------
# sra
#-------------------------------------------------------------------------

import inst_sra

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_sra.gen_basic_test     ) ,
  asm_test( inst_sra.gen_dest_dep_test  ) ,
  asm_test( inst_sra.gen_src0_dep_test  ) ,
  asm_test( inst_sra.gen_src1_dep_test  ) ,
  asm_test( inst_sra.gen_srcs_dep_test  ) ,
  asm_test( inst_sra.gen_srcs_dest_test ) ,
  asm_test( inst_sra.gen_value_test     ) ,
  asm_test( inst_sra.gen_random_test    ) ,
])
def test_sra( name, test, dump_vcd ):
  run_test( ProcBaseRTL, test, dump_vcd )

def test_sra_rand_delays( dump_vcd ):
  for i in xrange( 1 ):
    src_delay       = random.randint( 1, 5 )
    sink_delay      = random.randint( 1, 5 )
    mem_stall_prob  = random.uniform(0.0, 0.4)
    mem_latency     = random.randint( 1, 5 )
    run_test( ProcBaseRTL, inst_sra.gen_random_test, dump_vcd, 
              src_delay = src_delay, sink_delay = sink_delay, 
              mem_stall_prob = mem_stall_prob, 
              mem_latency = mem_latency
            )

#-------------------------------------------------------------------------
# srl
#-------------------------------------------------------------------------

import inst_srl

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_srl.gen_basic_test     ) ,
  asm_test( inst_srl.gen_dest_dep_test  ) ,
  asm_test( inst_srl.gen_src0_dep_test  ) ,
  asm_test( inst_srl.gen_src1_dep_test  ) ,
  asm_test( inst_srl.gen_srcs_dep_test  ) ,
  asm_test( inst_srl.gen_srcs_dest_test ) ,
  asm_test( inst_srl.gen_value_test     ) ,
  asm_test( inst_srl.gen_random_test    ) ,
])
def test_srl( name, test, dump_vcd ):
  run_test( ProcBaseRTL, test, dump_vcd )

def test_srl_rand_delays( dump_vcd ):
  for i in xrange( 1 ):
    src_delay       = random.randint( 1, 5 )
    sink_delay      = random.randint( 1, 5 )
    mem_stall_prob  = random.uniform(0.0, 0.4)
    mem_latency     = random.randint( 1, 5 )
    run_test( ProcBaseRTL, inst_srl.gen_random_test, dump_vcd, 
              src_delay = src_delay, sink_delay = sink_delay, 
              mem_stall_prob = mem_stall_prob, 
              mem_latency = mem_latency
            )

#-------------------------------------------------------------------------
# sll
#-------------------------------------------------------------------------

import inst_sll

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_sll.gen_basic_test     ) ,
  asm_test( inst_sll.gen_dest_dep_test  ) ,
  asm_test( inst_sll.gen_src0_dep_test  ) ,
  asm_test( inst_sll.gen_src1_dep_test  ) ,
  asm_test( inst_sll.gen_srcs_dep_test  ) ,
  asm_test( inst_sll.gen_srcs_dest_test ) ,
  asm_test( inst_sll.gen_value_test     ) ,
  asm_test( inst_sll.gen_random_test    ) ,
])
def test_sll( name, test, dump_vcd ):
  run_test( ProcBaseRTL, test, dump_vcd )

def test_sll_rand_delays( dump_vcd ):
  for i in xrange( 1 ):
    src_delay       = random.randint( 1, 5 )
    sink_delay      = random.randint( 1, 5 )
    mem_stall_prob  = random.uniform(0.0, 0.4)
    mem_latency     = random.randint( 1, 5 )
    run_test( ProcBaseRTL, inst_sll.gen_random_test, dump_vcd, 
              src_delay = src_delay, sink_delay = sink_delay, 
              mem_stall_prob = mem_stall_prob, 
              mem_latency = mem_latency
            )


