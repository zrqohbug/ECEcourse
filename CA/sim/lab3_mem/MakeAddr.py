from pymtl import *

class MakeAddr( Model ):

  def __init__( s, in_dtype, out_dtype ):

    s.in_ = InPort( in_dtype )
    s.out = OutPort( out_dtype )

    @s.combinational
    def comb_logic():
      s.out.value = concat( s.in_, Bits( 4, 0 ) )


