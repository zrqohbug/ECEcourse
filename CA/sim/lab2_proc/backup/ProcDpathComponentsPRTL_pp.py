#=========================================================================
# ProcDpathComponentsPRTL.py
#=========================================================================

from pymtl            import *
from TinyRV2InstPRTL  import *
from pclib.rtl        import arith
from lab1_imul        import IntMulAltRTL

#-------------------------------------------------------------------------
# Generate intermediate (imm) based on type
#-------------------------------------------------------------------------

class ImmGenPRTL( Model ):

  # Interface

  def __init__( s ):

    s.imm_type = InPort( 3 )
    s.inst     = InPort( 32 )
    s.imm      = OutPort( 32 )

    @s.combinational
    def comb_logic():
      # Always sext!

      if   s.imm_type == 0: # I-type

        s.imm.value = concat( sext( s.inst[ I_IMM ], 32 ) )

      elif s.imm_type == 1: # S-type

        s.imm.value = concat( sext( s.inst[ S_IMM1 ], 27 ), s.inst[ S_IMM0 ] )

      elif s.imm_type == 2: # B-type

        s.imm.value = concat( sext( s.inst[ B_IMM3 ], 20 ),
                                    s.inst[ B_IMM2 ],
                                    s.inst[ B_IMM1 ],
                                    s.inst[ B_IMM0 ],
                                    Bits( 1, 0 ) )

      elif s.imm_type == 3: # U-type

        s.imm.value = concat( s.inst[ U_IMM ], Bits( 12, 0 ) )

      elif s.imm_type == 4: # J-type

        s.imm.value = concat( sext( s.inst[ J_IMM3 ], 12 ),
					s.inst[ J_IMM2 ], 
					s.inst[ J_IMM1 ], 
					s.inst[ J_IMM0 ], 
					Bits( 1, 0 ))

      else: # Invalid immediate type!

        s.imm.value = Bits( 32, 0 )

#-------------------------------------------------------------------------
# ALU
#-------------------------------------------------------------------------

class AluPRTL( Model ):

  # Interface

  def __init__( s ):

    s.in0      = InPort ( 32 )
    s.in1      = InPort ( 32 )
    s.fn       = InPort ( 4 )

    s.out      = OutPort( 32 )
    s.ops_eq   = OutPort( 1 )
    s.ops_lt   = OutPort( 1 )
    s.ops_ltu  = OutPort( 1 )

  # Combinational Logic

    s.slt   = Wire( 32 )
    s.sra   = Wire( 32 )

    s.shamt = Wire( 5 )

    @s.combinational
    def comb_shamt_logic():
      s.shamt.value = s.in1 & 0x1f

    @s.combinational
    def comb_slt_logic():
      tmp = sext( s.in0, 33 ) - sext( s.in1, 33 )
      s.slt.value = Bits( 32, 1 ) if tmp[32] else Bits( 32, 0 )

    @s.combinational
    def comb_sra_logic():
      tmp = sext( s.in0, 64 ) >> s.shamt
      s.sra.value = tmp[ 0:32 ]

    @s.combinational
    def comb_logic():

      if   s.fn ==  0: s.out.value = s.in0 + s.in1          # ADD
      elif s.fn ==  1: s.out.value = s.in0 - s.in1          # SUB
      elif s.fn ==  2: s.out.value = s.in0 & s.in1          # AND
      elif s.fn ==  3: s.out.value = s.in0 | s.in1          # OR
      elif s.fn ==  4: s.out.value = s.in0 ^ s.in1          # XOR
      elif s.fn ==  5: s.out.value = s.slt                  # SLT
      elif s.fn ==  6: s.out.value = s.in0 < s.in1          # SLTU
      elif s.fn ==  7: s.out.value = s.sra                  # SRA
      elif s.fn ==  8: s.out.value = s.in0 >> s.shamt       # SRL
      elif s.fn ==  9: s.out.value = \
                Bits( 32, s.in0 << s.shamt, trunc = True )  # SLL
      elif s.fn == 10: s.out.value = \
                Bits( 32, s.in0 * s.in1, trunc = True )     # MUL
      elif s.fn == 11: s.out.value = s.in0                  # CP OP0
      elif s.fn == 12: s.out.value = s.in1                  # CP OP1
      elif s.fn == 13: s.out.value = \
                ( s.in0 + s.in1 ) & 0xfffffffe              # JALR

      else:            s.out.value = 0                      # Unknown

      s.ops_eq.value  = ( s.in0 == s.in1 )
      s.ops_lt.value  = ( s.slt[ 0 ] )
      s.ops_ltu.value = s.in0 < s.in1
