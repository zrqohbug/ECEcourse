from pymtl import *

class Repl( Model ):

  def __init__( s, in_dtype, factor ):

    s.in_ = InPort( in_dtype )
    s.out = OutPort( in_dtype * factor )

    @s.combinational
    def comb_logic():
      tmp = s.in_
      for i in xrange( factor-1 ):
        tmp = concat( tmp, s.in_ )
      s.out.value = tmp


