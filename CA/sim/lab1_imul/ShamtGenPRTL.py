#=======================================================================
# Shift Amount Generator RTL Model
# @desc: 
# This generator calculates how many bits to skip and gives the correct
# shamt parameter to shifters. 
#=======================================================================

from pymtl      import *
from pclib.rtl  import Adder, Mux, RightLogicalShifter, Subtractor

MUX_SEL_NBITS   = 1
MUX_SEL_ENCODER = 1
MUX_SEL_SKIP    = 0
MUX_SEL_X       = 0 

class ShamtGenPRTL( Model ):

  def __init__( s ):
    
    #==================================================================
    # Interfaces
    #==================================================================

    s.a               = InPort   ( 32 )
#    s.look_ahead_cnt  = InPort   ( 6 )

    s.shamt           = OutPort  ( 6 )

    #==================================================================
    # Structure
    #==================================================================

    # Substractor (s.a - 1) 

    s.sub             = m = Subtractor  ( 32 )

    s.sub_out         = Wire ( 32 )

    s.connect_pairs(
      m.in0,      s.a, 
      m.in1,      1, 
      m.out,      s.sub_out,
    )

    # Right shifter

    s.rshift          = m = RightLogicalShifter ( 32 )

    s.xor_out         = Wire ( 32 )
    s.xor_not_out     = Wire ( 32 )
    s.rshift_out      = Wire ( 32 )
    s.and_out         = Wire ( 32 )

    s.connect_pairs(
      m.in_,      s.xor_not_out,
      m.shamt,    1, 
      m.out,      s.rshift_out,
    )

    # Encoder
    
    s.encoder         = m = Encoder () 

    s.encoder_out     = Wire ( 6 )

    s.connect_pairs(
      m.in_,          s.and_out, 
      m.out,          s.encoder_out,
    )

    # MUX

    s.mux             = m = Mux ( 6, 2 )

    s.mux_sel         = Wire ( MUX_SEL_NBITS )

    s.connect_pairs(
      m.sel,                      s.mux_sel, 
      m.in_[ MUX_SEL_ENCODER ],   s.encoder_out, 
      m.in_[ MUX_SEL_SKIP ],      32,
#      m.in_[ MUX_SEL_SKIP ],      s.look_ahead_cnt,
      m.out,                      s.shamt,
    )

    #==================================================================
    # Combinational Logic
    #==================================================================
    
    @s.combinational
    def xor_block():
      s.xor_out.value       = s.a ^ s.sub_out
      s.xor_not_out.value   = ~( s.a ^ s.sub_out )

    @s.combinational
    def and_block(): 
      s.and_out.value       = s.rshift_out & s.xor_out

    @s.combinational
    def mux_sel_block():
      s.mux_sel.value       = s.encoder_out[0] | s.encoder_out[1] | \
                              s.encoder_out[2] | s.encoder_out[3] | \
                              s.encoder_out[4] | s.encoder_out[5]

class Encoder( Model ):

  def __init__( s ):
    
    s.in_   = InPort  ( 32 )
    s.out   = OutPort ( 6 )

    @s.combinational
    def output_block(): 
      s.out[0].value = \
                 s.in_[0] | s.in_[2] | s.in_[4] | s.in_[6] | s.in_[8] | \
                 s.in_[10] | s.in_[12] | s.in_[14] | s.in_[16] | \
                 s.in_[18] | s.in_[20] | s.in_[22] | s.in_[24] | \
                 s.in_[26] | s.in_[28] | s.in_[30]
      s.out[1].value = \
                 s.in_[1] | s.in_[2] | s.in_[5] | s.in_[6] | s.in_[9] | \
                 s.in_[10] | s.in_[13] | s.in_[14] | s.in_[17] | \
                 s.in_[18] | s.in_[21] | s.in_[22] | s.in_[25] | \
                 s.in_[26] | s.in_[29] | s.in_[30]
      s.out[2].value = \
                 s.in_[3] | s.in_[4] | s.in_[5] | s.in_[6] | s.in_[11] | \
                 s.in_[12] | s.in_[13] | s.in_[14] | s.in_[19] | \
                 s.in_[20] | s.in_[21] | s.in_[22] | s.in_[27] | \
                 s.in_[28] | s.in_[29] | s.in_[30]
      s.out[3].value = \
                 s.in_[7] | s.in_[8] | s.in_[9] | s.in_[10] | s.in_[11] | \
                 s.in_[12] | s.in_[13] | s.in_[14] | s.in_[23] | \
                 s.in_[24] | s.in_[25] | s.in_[26] | s.in_[27] | \
                 s.in_[28] | s.in_[29] | s.in_[30]
      s.out[4].value = \
                 s.in_[15] | s.in_[16] | s.in_[17] | s.in_[18] | \
                 s.in_[19] | s.in_[20] | s.in_[21] | s.in_[22] | \
                 s.in_[23] | s.in_[24] | s.in_[25] | s.in_[26] | \
                 s.in_[27] | s.in_[28] | s.in_[29] | s.in_[30]
      s.out[5].value = s.in_[31]

if __name__ == "__main__":
  a = ShamtGenPRTL()
