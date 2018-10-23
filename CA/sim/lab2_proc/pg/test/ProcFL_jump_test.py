#=========================================================================
# ProcFL_test.py
#=========================================================================

import pytest
import random

from pymtl   import *
from harness import *
from lab2_proc.ProcFL import ProcFL

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
  run_test( ProcFL, test, dump_vcd )

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
  run_test( ProcFL, test, dump_vcd )
