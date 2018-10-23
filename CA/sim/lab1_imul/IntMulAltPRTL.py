#=========================================================================
# Integer Multiplier Variable Latency RTL Model
#=========================================================================

# The alternative design skips any number of consecutive zero bits
# within less than a cycle. The cycles needed for the multiplication
# equals to the number of one bits in the binary representation of
# the multiplier. 

from pymtl        import *
from pclib.ifcs   import InValRdyBundle, OutValRdyBundle
from pclib.rtl    import Adder, Mux, Subtractor,\
                         LeftLogicalShifter, RightLogicalShifter
from pclib.rtl    import RegEn, Reg, RegRst

from ShamtGenPRTL import ShamtGenPRTL

# Mux constants

A_MUX_SEL_NBITS       = 1
A_MUX_SEL_IN          = 0
A_MUX_SEL_SHIFT       = 1
A_MUX_SEL_X           = 0

B_MUX_SEL_NBITS       = 1
B_MUX_SEL_IN          = 0
B_MUX_SEL_SHIFT       = 1
B_MUX_SEL_X           = 0

RES_MUX_SEL_NBITS     = 1
RES_MUX_SEL_ZERO      = 0
RES_MUX_SEL_ADD       = 1
RES_MUX_SEL_X         = 0

ADD_MUX_SEL_NBITS     = 1
ADD_MUX_SEL_ADD       = 0
ADD_MUX_SEL_RES       = 1
ADD_MUX_SEL_X         = 0

OUT_MUX_SEL_NBITS     = 1
OUT_MUX_SEL_POS       = 0
OUT_MUX_SEL_NEG       = 1
OUT_MUX_SEL_X         = 0

#======================================================================
# Integer Multiplier Data Path
#======================================================================

class IntMulAltDpathPRTL( Model ):

  def __init__( s ):
    
    #==================================================================
    # Interfaces
    #==================================================================

    s.req_msg_a  = InPort   ( 32 )
    s.req_msg_b  = InPort   ( 32 )
    s.resp_msg   = OutPort  ( 32 )

    # Control signals

    s.a_mux_sel         = InPort    ( A_MUX_SEL_NBITS )
    s.b_mux_sel         = InPort    ( B_MUX_SEL_NBITS )
    s.result_mux_sel    = InPort    ( RES_MUX_SEL_NBITS )
    s.add_mux_sel       = InPort    ( ADD_MUX_SEL_NBITS )
    s.result_en         = InPort    ( 1 )
    s.result_sign       = InPort    ( OUT_MUX_SEL_NBITS )

    # Status signals

    s.b_lsb             = OutPort   ( 1 )
    s.a_msb             = OutPort   ( 1 )
    s.b_msb             = OutPort   ( 1 )

    s.to_ctrl_shamt     = OutPort   ( 6 )

    # shamt input to shifters, calculated by ShamtGen

    s.shamt             = Wire      ( 6 )

    # Binary representation of the multiplier

    s.bit_string        = Wire      ( 32 )

    #==================================================================
    # Structure
    #==================================================================

    # A Mux

    s.in_a            = Wire( 32 )

    # Take the absolute value of the input 

    @s.combinational
    def sign_handling_a(): 
      s.in_a.value = s.req_msg_a if ~s.req_msg_a[31] \
                     else (~s.req_msg_a) + 1

    s.l_shift_out     = Wire( 32 )

    s.a_mux       = m = Mux( 32, 2 )

    s.connect_pairs(
      m.sel,                     s.a_mux_sel, 
      m.in_[ A_MUX_SEL_IN ],     s.in_a, 
      m.in_[ A_MUX_SEL_SHIFT ],  s.l_shift_out,
    )

    # A Register

    s.a_reg       = m = Reg( 32 )

    s.connect( m.in_, s.a_mux.out )

    # Left Shifter

    s.l_shift     = m = LeftLogicalShifter( 32, 6 )

    s.connect_pairs( 
      m.in_,    s.a_reg.out,
      m.shamt,  s.shamt, 
      m.out,    s.l_shift_out,
    )

    # B Mux

    s.in_b            = Wire( 32 )

    # Take the absolute value of the input

    @s.combinational
    def sign_handling_b(): 
      s.in_b.value = s.req_msg_b if ~s.req_msg_b[31] \
                     else (~s.req_msg_b) + 1

    s.r_shift_out     = Wire( 32 )

    s.b_mux       = m = Mux( 32, 2 )

    s.connect_pairs(
      m.sel,                     s.b_mux_sel, 
      m.in_[ B_MUX_SEL_IN ],     s.in_b, 
      m.in_[ B_MUX_SEL_SHIFT ],  s.r_shift_out,  
    )

    # B Register

    s.b_reg       = m = Reg( 32 )

    s.connect( m.in_, s.b_mux.out )

    # Take the higher 31 bits and add 0 in the high order
    # The ShamtGen module will generate the appropriate shamt
    # according to the number of consecutive zeros in lower s.bit_string

    @s.combinational
    def bit_string_block(): 
      s.bit_string.value = concat( Bits( 1, 0 ), s.b_reg.out[1:32] )

    # Right Shifter

    s.r_shift     = m = RightLogicalShifter( 32, 6 )

    s.connect_pairs(
      m.in_,    s.b_reg.out,  
      m.shamt,  s.shamt,
      m.out,    s.r_shift_out, 
    )

    # Result Mux

    s.add_mux_out     = Wire( 32 )

    s.result_mux  = m = Mux( 32, 2 )

    s.connect_pairs(
      m.sel,                      s.result_mux_sel, 
      m.in_[ RES_MUX_SEL_ZERO ],  0,
      m.in_[ RES_MUX_SEL_ADD ],   s.add_mux_out,
    )

    # Result Register

    s.res_reg     = m = RegEn( 32 )

    s.connect_pairs(
      m.in_,  s.result_mux.out, 
      m.en,   s.result_en
    )

    # Adder

    s.adder       = m = Adder( 32 )

    s.connect_pairs(
      m.in0,  s.a_reg.out, 
      m.in1,  s.res_reg.out,
      m.cin,  0,
    )

    # Add Mux

    s.add_mux     = m = Mux( 32, 2 )

    s.connect_pairs(
      m.sel,                      s.add_mux_sel, 
      m.in_[ ADD_MUX_SEL_ADD ],   s.adder.out, 
      m.in_[ ADD_MUX_SEL_RES ],   s.res_reg.out,
      m.out,                      s.add_mux_out,
    )

    # ShamtGen

    s.shamt_gen   = m = ShamtGenPRTL()

    s.connect_pairs(
      m.a,                        s.bit_string, 
      m.shamt,                    s.shamt,
    )

    # Forward shamt to control unit so the counter can update 
    # accordingly

    @s.combinational
    def to_ctrl_shamt_block():
      s.to_ctrl_shamt.value = s.shamt

    # Output MUX
    s.res_neg       = Wire( 32 )

    # Generate -res in case the result is negative

    @s.combinational
    def twos_compl_block():
      s.res_neg.value = (~s.res_reg.out) + 1

    s.out_mux       = m = Mux( 32, 2 )

    s.connect_pairs(
      m.sel,                      s.result_sign, 
      m.in_[ OUT_MUX_SEL_POS ],   s.res_reg.out,
      m.in_[ OUT_MUX_SEL_NEG ],   s.res_neg,
      m.out,                      s.resp_msg,
    )

    # Connect status signals

    s.connect( s.b_reg.out[0], s.b_lsb )
    s.connect( s.req_msg_a[31], s.a_msb )
    s.connect( s.req_msg_b[31], s.b_msb )

#======================================================================
# Integer Multiplier Control Unit
#======================================================================

class IntMulAltCtrlPRTL( Model ):

  # Constructor

  def __init__( s ):
    
    #==================================================================
    # Interface
    #==================================================================

    s.req_val   = InPort  ( 1 )
    s.req_rdy   = OutPort ( 1 )

    s.resp_val  = OutPort ( 1 )
    s.resp_rdy  = InPort  ( 1 )

    # Control signals

    s.a_mux_sel       = OutPort ( A_MUX_SEL_NBITS )
    s.b_mux_sel       = OutPort ( B_MUX_SEL_NBITS )
    s.result_mux_sel  = OutPort ( RES_MUX_SEL_NBITS )
    s.add_mux_sel     = OutPort ( ADD_MUX_SEL_NBITS )
    s.result_en       = OutPort ( 1 )
    s.result_sign     = OutPort ( OUT_MUX_SEL_NBITS )

    # Status signals

    s.shamt           = InPort  ( 6 )

    s.b_lsb           = InPort  ( 1 )
    s.a_msb           = InPort  ( 1 )
    s.b_msb           = InPort  ( 1 )

    # State elements

    s.STATE_IDLE  = 0
    s.STATE_CALC  = 1
    s.STATE_DONE  = 2

    s.state = RegRst( 2, reset_value = s.STATE_IDLE )
    
    # Counter: how many bits have already been scanned

    s.counter = RegRst( 6, reset_value = 1 )

    # Sign register

    s.result_sign_reg = RegRst( 1, reset_value = 0 )

    # Store the sign of the result at I state then use it as MUX 
    # selection during output

    @s.combinational
    def result_sign_out_block():
      s.result_sign.value = s.result_sign_reg.out

    #==================================================================
    # State Transistion Logic
    #==================================================================

    @s.combinational
    def state_transistions(): 
      
      curr_state = s.state.out
      next_state = s.state.out

      # Transistions out of IDLE state

      if ( curr_state == s.STATE_IDLE ):
        if ( s.req_val and s.req_rdy ):
          next_state = s.STATE_CALC

      # Transistions out of CALC state

      if ( curr_state == s.STATE_CALC ):
        if ( s.counter.out >= 32 ):
          next_state = s.STATE_DONE

      # Transistions out of DONE state

      if ( curr_state == s.STATE_DONE ):
        if ( s.resp_val and s.resp_rdy ):
          next_state = s.STATE_IDLE

      s.state.in_.value = next_state

    #==================================================================
    # Output Logic
    #==================================================================

    s.add_mux_sel_value           = Wire( ADD_MUX_SEL_NBITS )

    # Genereate add MUX selection value 

    @s.combinational
    def add_mux_sel_block(): 
      if ( s.counter.out >= 32 ):
        s.add_mux_sel_value.value = ADD_MUX_SEL_RES
      else:
        if ( s.b_lsb ):
          s.add_mux_sel_value.value = ADD_MUX_SEL_ADD
        else:
          s.add_mux_sel_value.value = ADD_MUX_SEL_RES
        

    # Generate control signals

    @s.combinational
    def state_outputs():
      
      curr_state = s.state.out

      if ( curr_state == s.STATE_IDLE ):
        s.req_rdy.value               = 1
        s.resp_val.value              = 0
        s.a_mux_sel.value             = A_MUX_SEL_IN
        s.b_mux_sel.value             = B_MUX_SEL_IN
        s.result_mux_sel.value        = RES_MUX_SEL_ZERO
        s.add_mux_sel.value           = ADD_MUX_SEL_ADD
        s.result_en.value             = 1
        s.counter.in_.value           = 0
        s.result_sign_reg.in_.value   = s.a_msb ^ s.b_msb

      elif ( curr_state == s.STATE_CALC ):
        s.req_rdy.value               = 0
        s.resp_val.value              = 0
        s.a_mux_sel.value             = A_MUX_SEL_SHIFT
        s.b_mux_sel.value             = B_MUX_SEL_SHIFT
        s.result_mux_sel.value        = RES_MUX_SEL_ADD
        s.add_mux_sel.value           = s.add_mux_sel_value 
        s.result_en.value             = 1
        s.counter.in_.value           = s.counter.out + s.shamt
        s.result_sign_reg.in_.value   = s.result_sign_reg.out

      elif ( curr_state == s.STATE_DONE ):
        s.req_rdy.value               = 0
        s.resp_val.value              = 1
        s.a_mux_sel.value             = A_MUX_SEL_X
        s.b_mux_sel.value             = B_MUX_SEL_X
        s.result_mux_sel.value        = RES_MUX_SEL_X
        s.add_mux_sel.value           = ADD_MUX_SEL_X
        s.result_en.value             = 0
        s.counter.in_.value           = s.counter.out
        s.result_sign_reg.in_.value   = s.result_sign_reg.out

      # Complete all cases to avoid inferring latches

      else:
        s.req_rdy.value               = 0
        s.resp_val.value              = 0
        s.a_mux_sel.value             = A_MUX_SEL_X
        s.b_mux_sel.value             = B_MUX_SEL_X
        s.result_mux_sel.value        = RES_MUX_SEL_X
        s.add_mux_sel.value           = ADD_MUX_SEL_X
        s.result_en.value             = 0
        s.counter.in_.value           = 0
        s.result_sign_reg.in_.value   = 0

#=========================================================================
# Integer Multiplier Variable Latency
#=========================================================================

class IntMulAltPRTL( Model ):

  # Constructor

  def __init__( s ):

    # Interface

    s.req    = InValRdyBundle  ( Bits(64) )
    s.resp   = OutValRdyBundle ( Bits(32) )

    s.dpath  = IntMulAltDpathPRTL()
    s.ctrl   = IntMulAltCtrlPRTL()

    s.connect( s.req.msg[0:32],       s.dpath.req_msg_a )
    s.connect( s.req.msg[32:64],      s.dpath.req_msg_b )

    s.connect( s.req.val,             s.ctrl.req_val )
    s.connect( s.req.rdy,             s.ctrl.req_rdy )

    s.connect( s.resp.val,            s.ctrl.resp_val )
    s.connect( s.resp.rdy,            s.ctrl.resp_rdy )

    s.connect( s.dpath.to_ctrl_shamt, s.ctrl.shamt )

    s.connect( s.dpath.resp_msg,      s.resp.msg )

    s.connect_auto( s.dpath,          s.ctrl )

  # Line tracing

  def line_trace( s ):

    state_str = "?"
    
    if ( s.ctrl.state.out == s.ctrl.STATE_IDLE ):
      state_str = "I"
    if ( s.ctrl.state.out == s.ctrl.STATE_CALC ):
      if ( s.ctrl.counter.out < 32):
        state_str = "C+"
      else:
        state_str = "C"
    if ( s.ctrl.state.out == s.ctrl.STATE_DONE ):
      state_str = "D"

    line_trace_str = "a:{} b:{} shamt:{} state:{}".format(
      s.dpath.a_reg.out, 
      s.dpath.b_reg.out, 
      s.dpath.shamt,
      state_str,
    )

    return "{}({}){}".format(
      s.req,
      line_trace_str,
      s.resp,
    )

