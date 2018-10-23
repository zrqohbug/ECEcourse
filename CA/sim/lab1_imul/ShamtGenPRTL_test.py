import pytest

from pymtl        import *
from pclib.test   import run_test_vector_sim

from ShamtGenPRTL import ShamtGenPRTL

def test():
  run_test_vector_sim( ShamtGenPRTL(), [
    ('a       shamt*'), 
    [0b11011,                    1], 
    [0b11000,                    4], 
    [0b00000,                    32], 
    [0b00110,                     2], 
    [0b10101,                     1], 
    [0b00000,                    32],
    [0b11111,                    1],
    [0x40000000,                    31],
    [0x40000000,                    31],
  ] )
