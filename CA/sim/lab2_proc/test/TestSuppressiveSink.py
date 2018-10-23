#=======================================================================
# TestSuppressiveSink
#=======================================================================

from pymtl      import *
from pclib.ifcs import InValRdyBundle
from copy       import deepcopy

class TestSuppressiveSinkError( Exception ):
  pass

#-----------------------------------------------------------------------
# TestSuppressiveSink
#-----------------------------------------------------------------------

class TestSuppressiveSink( Model ):

  def __init__( s, dtype, out_buffer, num_regs ):

    s.in_  = InValRdyBundle( dtype )
    s.done = OutPort       ( 1     )

    s.idx  = 0

    s.num_regs = num_regs

    @s.tick
    def tick():

      # Handle reset

      if s.reset:
        s.in_.rdy.next = False
        s.done   .next = False
        return

      # At the end of the cycle, we AND together the val/rdy bits to
      # determine if the input message transaction occured

      in_go = s.in_.val and s.in_.rdy

      # If the input transaction occured, write it to the output buffer
      # then increment the index.

      if in_go:

        out_buffer.append( deepcopy(s.in_.msg) )

        s.idx = s.idx + 1

      # Set the ready and done signals.

      if ( s.idx < s.num_regs ):
        s.in_.rdy.next = True
        s.done   .next = False
      else:
        s.in_.rdy.next = False
        s.done   .next = True


  def line_trace( s ):
    return "{} ({:2})".format( s.in_, s.idx )

