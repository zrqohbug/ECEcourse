#=========================================================================
# BlockingCacheAltPRTL.py
#=========================================================================

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.ifcs import MemMsg, MemReqMsg, MemRespMsg

from BlockingCacheAltCtrlPRTL  import BlockingCacheAltCtrlPRTL
from BlockingCacheAltDpathPRTL import BlockingCacheAltDpathPRTL

# Note on num_banks:
# In a multi-banked cache design, cache lines are interleaved to
# different cache banks, so that consecutive cache lines correspond to a
# different bank. The following is the addressing structure in our
# four-banked data caches:
#
# +--------------------------+--------------+--------+--------+--------+
# |        22b               |     4b       |   2b   |   2b   |   2b   |
# |        tag               |   index      |bank idx| offset | subwd  |
# +--------------------------+--------------+--------+--------+--------+
#
# We will compose four-banked cache in lab5 multi-core lab.

class BlockingCacheAltPRTL( Model ):

  def __init__( s, num_banks=0 ):

    # Parameters
    idx_shamt       = clog2( num_banks ) if num_banks > 0 else 0
    size            = 256  # 256 bytes
    opaque_nbits    = 8    # 8-bit opaque field
    addr_nbits      = 32   # 32-bit address
    data_nbits      = 32   # 32-bit data access
    cacheline_nbits = 128  # 128-bit cacheline

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    # Proc <-> Cache

    s.cachereq  = InValRdyBundle ( MemReqMsg(opaque_nbits, addr_nbits, data_nbits)  )
    s.cacheresp = OutValRdyBundle( MemRespMsg(opaque_nbits, data_nbits) )

    # Cache <-> Mem

    s.memreq    = OutValRdyBundle( MemReqMsg(opaque_nbits, addr_nbits, cacheline_nbits)  )
    s.memresp   = InValRdyBundle ( MemRespMsg(opaque_nbits, cacheline_nbits) )

    s.ctrl      = BlockingCacheAltCtrlPRTL ( idx_shamt )
    s.dpath     = BlockingCacheAltDpathPRTL( idx_shamt )

    # Ctrl

    s.connect_pairs(
      s.ctrl.cachereq_val,  s.cachereq.val, 
      s.ctrl.cachereq_rdy,  s.cachereq.rdy, 
      s.ctrl.cacheresp_val, s.cacheresp.val, 
      s.ctrl.cacheresp_rdy, s.cacheresp.rdy, 
      s.ctrl.memreq_val,    s.memreq.val, 
      s.ctrl.memreq_rdy,    s.memreq.rdy, 
      s.ctrl.memresp_val,   s.memresp.val, 
      s.ctrl.memresp_rdy,   s.memresp.rdy
    )

    # Dpath

    s.connect_pairs(
      s.dpath.cachereq_msg,  s.cachereq.msg, 
      s.dpath.cacheresp_msg, s.cacheresp.msg, 
      s.dpath.memreq_msg,    s.memreq.msg, 
      s.dpath.memresp_msg,   s.memresp.msg
    )

    # Ctrl <-> Dpath

    s.connect_auto( s.ctrl, s.dpath )

    # State dictionary

    s.state_map = {
      s.ctrl.STATE_IDLE              : 'I',
      s.ctrl.STATE_TAG_CHECK         : 'TC',
      s.ctrl.STATE_INIT_DATA_ACCESS  : 'IN',
      s.ctrl.STATE_READ_DATA_ACCESS  : 'RD',
      s.ctrl.STATE_WRITE_DATA_ACCESS : 'WD',
      s.ctrl.STATE_EVICT_PREPARE     : 'EP',
      s.ctrl.STATE_EVICT_REQUEST     : 'ER',
      s.ctrl.STATE_EVICT_WAIT        : 'EW',
      s.ctrl.STATE_REFILL_REQUEST    : 'RR',
      s.ctrl.STATE_REFILL_WAIT       : 'RW',
      s.ctrl.STATE_REFILL_UPDATE     : 'RU',
      s.ctrl.STATE_WAIT              : 'W'
    }

  def line_trace( s ):

    state_str = s.state_map[ s.ctrl.state.out.uint() ]

    if s.ctrl.cachereq_type == MemReqMsg.TYPE_READ:
      type_str = 'read'
    elif s.ctrl.cachereq_type == MemReqMsg.TYPE_WRITE:
      type_str = 'write'
    else:
      type_str = 'write_init'

    addr_str = hex( s.ctrl.cachereq_addr )

    if s.ctrl.hit == 0:
      hit_str = 'miss'
    else:
      hit_str = 'hit'

    return state_str + "|" + type_str + "|" + addr_str + "|" + hit_str


