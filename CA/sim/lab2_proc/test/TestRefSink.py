from pymtl      import *
from pclib.test import TestRandomDelay
from pclib.ifcs import InValRdyBundle, OutValRdyBundle

from TestSuppressiveSink import TestSuppressiveSink

class TestRefSink( Model ):

  def __init__( s, dtype, output, num_regs, max_random_delay = 0 ):

    s.in_  = InValRdyBundle( dtype )
    s.done = OutPort       ( 1     )

    # Set up output buffer

    # Instantiate modules

    s.delay = TestRandomDelay( dtype, max_random_delay )
    s.sink  = TestSuppressiveSink ( dtype, output, num_regs )

    # Connect the input ports -> random delay -> sink

    s.connect( s.in_,       s.delay.in_ )
    s.connect( s.delay.out, s.sink.in_  )

    # Connect test sink done signal to output port

    s.connect( s.sink.done, s.done )

  def line_trace( s ):

    return "{}".format( s.in_ )

