#=========================================================================
# BlockingCacheAltDpathPRTL.py
#=========================================================================

from pymtl      import *
from pclib.ifcs import MemMsg, MemReqMsg, MemRespMsg
from pclib.rtl.arith import EqComparator
from pclib.rtl.SRAMs import SRAMBitsComb_rst_1rw, SRAMBytesComb_rst_1rw
from pclib.rtl.regs  import RegEnRst
from pclib.rtl.Mux   import Mux

from Repl     import Repl
from MakeAddr import MakeAddr

class BlockingCacheAltDpathPRTL( Model ):

  def __init__( s, idx_shamt ):

    # Parameters

    o   = 8   # Short name for opaque bitwidth
    abw = 32  # Short name for addr bitwidth
    dbw = 32  # Short name for data bitwidth
    clw = 128 # Short name for cacheline bitwidth
    nbl = 16  # Short name for number of cache blocks, 256*8/128 = 16
    idw = 3   # Short name for index width, clog2(16)-1 = 3 (-1 for 2-way)
    ofw = 4   # Short name for offset bit width, clog2(128/8) = 4
    nby = 16  # Short name for number of cache blocks per way, 16/1 = 16
    # In the lab, to simplify things, we always use all bits except for
    # the offset bits to represent the tag instead of storing the 25-bit
    # tag and concatenate everytime with the index bits and even the bank
    # bits to get the address of a cacheline
    tgw = 28  # Short name for tag bit width, 32-4 = 28

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    # Cache request

    s.cachereq_msg  = InPort ( MemReqMsg(o, abw, dbw) )

    # Cache response

    s.cacheresp_msg = OutPort( MemRespMsg(o, dbw) )

    # Memory request

    s.memreq_msg    = OutPort( MemReqMsg(o, abw, clw) )

    # Memory response

    s.memresp_msg   = InPort ( MemRespMsg(o, clw) )

    # From Ctrl

    s.cachereq_en         = InPort( 1 )
    s.memresp_en         = InPort( 1 )
    s.read_data_reg_en    = InPort( 1 )
    s.evict_addr_reg_en   = InPort( 1 )

    # We'll have split tag arrays and unified data array

    s.tag_array_wen0      = InPort( 1 )
    s.tag_array_wen1      = InPort( 1 )
    s.data_array_wen      = InPort( 1 )
    s.data_array_wben     = InPort( clw/8 )

    s.write_data_mux_sel  = InPort( 1 )
    s.memreq_addr_mux_sel = InPort( 1 )
    s.read_word_mux_sel   = InPort( 3 )

    s.hit                 = InPort( 2 )
    s.cacheresp_type      = InPort( 3 )
    s.memreq_type         = InPort( 3 )

    s.way_mux_sel         = InPort( 1 ) # which tag array to read from?
    s.victim              = InPort( 1 ) # Victim for evict and refill path
    s.victim_mux_sel      = InPort( 1 ) # Evict/refill or RD/WD?
    s.tag_match1_reg_en   = InPort( 1 ) # When to register tag_match1?

    # To Ctrl
    
    s.cachereq_type = OutPort( 3 )
    s.cachereq_addr = OutPort( 32 )

    s.tag_match0    = OutPort( 1 )
    s.tag_match1    = OutPort( 1 )

    s.which_way     = OutPort( 1 )

    #---------------------------------------------------------------------
    # Componenet definitions
    #---------------------------------------------------------------------

    s.cachereq_opaque_reg = m = RegEnRst( dtype = 8 )
    s.connect_pairs(
      m.en,  s.cachereq_en, 
      m.in_, s.cachereq_msg.opaque, 
      m.out, s.cacheresp_msg.opaque
    )

    s.cachereq_type_reg   = m = RegEnRst( dtype = 3 )
    s.connect_pairs(
      m.en,  s.cachereq_en, 
      m.in_, s.cachereq_msg.type_, 
      m.out, s.cachereq_type
    )

    s.cachereq_addr_reg   = m = RegEnRst( dtype = 32 )
    s.connect_pairs(
      m.en,  s.cachereq_en, 
      m.in_, s.cachereq_msg.addr, 
      m.out, s.cachereq_addr
    )

    s.cachereq_data_reg   = m = RegEnRst( dtype = 32 )
    s.connect_pairs(
      m.en,  s.cachereq_en, 
      m.in_, s.cachereq_msg.data
    )

    s.memresp_data_reg    = m = RegEnRst( dtype = 128 )
    s.connect_pairs(
      m.en,  s.memresp_en, 
      m.in_, s.memresp_msg.data
    )

    s.evict_addr_reg      = m = RegEnRst( dtype = 32 )
    s.connect_pairs(
      m.en,  s.evict_addr_reg_en
    )

    s.tag_array0          = m = SRAMBitsComb_rst_1rw(
      num_entries = 8, 
      data_nbits  = 28
    )
    s.connect_pairs(
      m.wen,   s.tag_array_wen0, 
      m.addr,  s.cachereq_addr_reg.out[ 4+idx_shamt:7+idx_shamt ],
      m.wdata, s.cachereq_addr_reg.out[ 4:32 ]
    )

    s.tag_array1          = m = SRAMBitsComb_rst_1rw(
      num_entries = 8, 
      data_nbits  = 28
    )
    s.connect_pairs(
      m.wen,   s.tag_array_wen1, 
      m.addr,  s.cachereq_addr_reg.out[ 4+idx_shamt:7+idx_shamt ],
      m.wdata, s.cachereq_addr_reg.out[ 4:32 ]
    )

    s.data_array          = m = SRAMBytesComb_rst_1rw(
      num_entries = 16, 
      num_nbytes  = 16
    )
    s.connect_pairs(
      m.wen,         s.data_array_wen, 
      m.wben,        s.data_array_wben,
      m.addr[ 0:3 ], s.cachereq_addr_reg.out[ 4+idx_shamt:7+idx_shamt ]
    )

    s.read_data_reg       = m = RegEnRst( dtype = 128 )
    s.connect_pairs(
      m.en,  s.read_data_reg_en, 
      m.in_, s.data_array.rdata
    )

    s.cachereq_data_repl  = m = Repl( in_dtype = 32, factor = 4 )
    s.connect_pairs(
      m.in_, s.cachereq_data_reg.out
    )

    s.write_data_mux      = m = Mux( dtype = 128, nports = 2 )
    s.connect_pairs(
      m.in_[ 0 ], s.cachereq_data_repl.out, 
      m.in_[ 1 ], s.memresp_data_reg.out, 
      m.sel,      s.write_data_mux_sel,
      m.out,      s.data_array.wdata
    )

    s.tag_comparator0     = m = EqComparator( nbits = 28 )
    s.connect_pairs(
      m.in0, s.cachereq_addr_reg.out[ 4:32 ],
      m.in1, s.tag_array0.rdata, 
      m.out, s.tag_match0
    )

    s.tag_comparator1     = m = EqComparator( nbits = 28 )
    s.connect_pairs(
      m.in0, s.cachereq_addr_reg.out[ 4:32 ],
      m.in1, s.tag_array1.rdata, 
      m.out, s.tag_match1
    )

    s.tag_match1_reg      = m = RegEnRst( dtype = 1 )
    s.connect_pairs(
      m.in_, s.tag_comparator1.out, 
      m.en,  s.tag_match1_reg_en,
      m.out, s.which_way
    )

    s.victim_mux          = m = Mux( dtype = 1, nports = 2 )
    s.connect_pairs(
      m.in_[ 0 ], s.victim, 
      m.in_[ 1 ], s.tag_match1_reg.out, 
      m.sel,      s.victim_mux_sel,
      m.out,      s.data_array.addr[ 3:4 ]
    )

    s.way_mux             = m = Mux( dtype = 28, nports = 2 )
    s.connect_pairs(
      m.in_[ 0 ], s.tag_array0.rdata, 
      m.in_[ 1 ], s.tag_array1.rdata,
      m.sel,      s.way_mux_sel
    )

    s.evict_mkaddr        = m = MakeAddr( in_dtype = 28, out_dtype = 32 )
    s.connect_pairs(
      m.in_, s.way_mux.out, 
      m.out, s.evict_addr_reg.in_
    )

    s.memreq_mkaddr       = m = MakeAddr( in_dtype = 28, out_dtype = 32 )
    s.connect_pairs(
        m.in_, s.cachereq_addr_reg.out[ 4:32 ]
    )

    s.memreq_addr_mux     = m = Mux( dtype = 32, nports = 2 )
    s.connect_pairs(
      m.in_[ 0 ], s.evict_addr_reg.out, 
      m.in_[ 1 ], s.memreq_mkaddr.out, 
      m.sel,      s.memreq_addr_mux_sel
    )

    s.read_word_mux       = m = Mux( dtype = 32, nports = 5 )
    s.connect_pairs(
      m.in_[ 0 ], s.read_data_reg.out[ 96:128 ], 
      m.in_[ 1 ], s.read_data_reg.out[ 64:96  ], 
      m.in_[ 2 ], s.read_data_reg.out[ 32:64  ], 
      m.in_[ 3 ], s.read_data_reg.out[ 0:32   ], 
      m.in_[ 4 ], 0, 
      m.sel,      s.read_word_mux_sel
    )

    #---------------------------------------------------------------------
    # Connect output interfaces and signals
    #---------------------------------------------------------------------
    
    # cacheresp_msg

    s.connect_pairs(
      s.cacheresp_msg.type_, s.cacheresp_type, 
      s.cacheresp_msg.len,   0, 
      s.cacheresp_msg.test,  s.hit, 
      s.cacheresp_msg.data,  s.read_word_mux.out
    )

    # memreq_msg

    s.connect_pairs(
      s.memreq_msg.opaque, 0,
      s.memreq_msg.type_,  s.memreq_type, 
      s.memreq_msg.len,    0, 
      s.memreq_msg.addr,   s.memreq_addr_mux.out, 
      s.memreq_msg.data,   s.read_data_reg.out
    )


