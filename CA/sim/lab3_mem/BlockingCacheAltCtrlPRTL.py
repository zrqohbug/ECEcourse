#=========================================================================
# BlockingCacheAltCtrlPRTL.py
#=========================================================================

from pymtl      import *

from pclib.ifcs             import MemMsg, MemReqMsg, MemRespMsg
from pclib.rtl.RegisterFile import RegisterFile
from pclib.rtl.regs         import RegRst

class BlockingCacheAltCtrlPRTL( Model ):

  def __init__( s, idx_shamt ):

    # Parameters

    abw = 32  # Short name for addr bitwidth
    dbw = 32  # Short name for data bitwidth
    clw = 128 # Short name for cacheline bitwidth
    nbl = 16  # Short name for number of cache blocks, 256*8/128 = 16
    idw = 3   # Short name for index width, clog2(16) = 4
    ofw = 4   # Short name for offset bit width, clog2(128/8) = 4
    nby = 8   # Short name for number of cache blocks per way, 16/2 = 8

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    # Cache request

    s.cachereq_val  = InPort ( 1 )
    s.cachereq_rdy  = OutPort( 1 )

    # Cache response

    s.cacheresp_val = OutPort( 1 )
    s.cacheresp_rdy = InPort ( 1 )

    # Memory request

    s.memreq_val    = OutPort( 1 )
    s.memreq_rdy    = InPort ( 1 )

    # Memory response

    s.memresp_val   = InPort ( 1 )
    s.memresp_rdy   = OutPort( 1 )

    # From Dpath
    
    s.cachereq_type = InPort( 3 )
    s.cachereq_addr = InPort( 32 )

    s.tag_match0    = InPort( 1 )
    s.tag_match1    = InPort( 1 )

    s.which_way     = InPort( 1 )

    # To Dpath

    s.cachereq_en         = OutPort( 1 )
    s.memresp_en         = OutPort( 1 )
    s.read_data_reg_en    = OutPort( 1 )
    s.evict_addr_reg_en   = OutPort( 1 )

    s.tag_array_wen0      = OutPort( 1 )
    s.tag_array_wen1      = OutPort( 1 )
    s.data_array_wen      = OutPort( 1 )
    s.data_array_wben     = OutPort( clw/8 )

    s.write_data_mux_sel  = OutPort( 1 )
    s.memreq_addr_mux_sel = OutPort( 1 )
    s.read_word_mux_sel   = OutPort( 3 )

    s.hit                 = OutPort( 2 )
    s.cacheresp_type      = OutPort( 3 )
    s.memreq_type         = OutPort( 3 )

    s.way_mux_sel         = OutPort( 1 ) # which tag array to read from?
    s.victim              = OutPort( 1 ) # Victim for evict and refill path
    s.victim_mux_sel      = OutPort( 1 ) # Evict/refill or RD/WD?
    s.tag_match1_reg_en   = OutPort( 1 ) # When to register tag_match1?

    #---------------------------------------------------------------------
    # State definitions
    #---------------------------------------------------------------------

    s.STATE_IDLE              = 0
    s.STATE_TAG_CHECK         = 1
    s.STATE_INIT_DATA_ACCESS  = 2
    s.STATE_READ_DATA_ACCESS  = 3
    s.STATE_WRITE_DATA_ACCESS = 4
    s.STATE_EVICT_PREPARE     = 5
    s.STATE_EVICT_REQUEST     = 6
    s.STATE_EVICT_WAIT        = 7
    s.STATE_REFILL_REQUEST    = 8
    s.STATE_REFILL_WAIT       = 9
    s.STATE_REFILL_UPDATE     = 10
    s.STATE_WAIT              = 11

    #---------------------------------------------------------------------
    # Component definitions
    #---------------------------------------------------------------------

    s.state = RegRst( 4, reset_value = s.STATE_IDLE )

    s.is_valid0     = Wire( 1 )
    s.val_rf_wdata0 = Wire( 1 )
    s.val_rf_wen0   = Wire( 1 )

    s.val_rf0 = m = RegisterFile( dtype = 1, nregs = nbl/2 )
    s.connect_pairs(
      m.rd_addr[ 0 ], s.cachereq_addr[ 4+idx_shamt:7+idx_shamt ], 
      m.rd_data[ 0 ], s.is_valid0, 
      m.wr_addr,      s.cachereq_addr[ 4+idx_shamt:7+idx_shamt ], 
      m.wr_data,      s.val_rf_wdata0,
      m.wr_en,        s.val_rf_wen0
    )

    s.is_valid1     = Wire( 1 )
    s.val_rf_wdata1 = Wire( 1 )
    s.val_rf_wen1   = Wire( 1 )

    s.val_rf1 = m = RegisterFile( dtype = 1, nregs = nbl/2 )
    s.connect_pairs(
      m.rd_addr[ 0 ], s.cachereq_addr[ 4+idx_shamt:7+idx_shamt ], 
      m.rd_data[ 0 ], s.is_valid1, 
      m.wr_addr,      s.cachereq_addr[ 4+idx_shamt:7+idx_shamt ], 
      m.wr_data,      s.val_rf_wdata1,
      m.wr_en,        s.val_rf_wen1
    )

    s.is_dirty0       = Wire( 1 )
    s.dirty_rf_wdata0 = Wire( 1 )
    s.dirty_rf_wen0   = Wire( 1 )

    s.dirty_rf0 = m = RegisterFile( dtype = 1, nregs = nbl/2 ) 
    s.connect_pairs(
      m.rd_addr[ 0 ], s.cachereq_addr[ 4+idx_shamt:7+idx_shamt ],
      m.rd_data[ 0 ], s.is_dirty0, 
      m.wr_addr,      s.cachereq_addr[ 4+idx_shamt:7+idx_shamt ], 
      m.wr_data,      s.dirty_rf_wdata0,
      m.wr_en,        s.dirty_rf_wen0
    )

    s.is_dirty1       = Wire( 1 )
    s.dirty_rf_wdata1 = Wire( 1 )
    s.dirty_rf_wen1   = Wire( 1 )

    s.dirty_rf1 = m = RegisterFile( dtype = 1, nregs = nbl/2 ) 
    s.connect_pairs(
      m.rd_addr[ 0 ], s.cachereq_addr[ 4+idx_shamt:7+idx_shamt ],
      m.rd_data[ 0 ], s.is_dirty1, 
      m.wr_addr,      s.cachereq_addr[ 4+idx_shamt:7+idx_shamt ], 
      m.wr_data,      s.dirty_rf_wdata1,
      m.wr_en,        s.dirty_rf_wen1
    )

    s.used = Wire( 1 )
    s.used_rf_wdata = Wire( 1 )
    s.used_rf_wen = Wire( 1 )

    s.used_array = m = RegisterFile( dtype = 1, nregs = nbl/2 )
    s.connect_pairs(
      m.rd_addr[ 0 ], s.cachereq_addr[ 4+idx_shamt:7+idx_shamt ],
      m.rd_data[ 0 ], s.used, 
      m.wr_addr,      s.cachereq_addr[ 4+idx_shamt:7+idx_shamt ],
      m.wr_data,      s.used_rf_wdata, 
      m.wr_en,        s.used_rf_wen
    )

    s.data_byte_en    = Wire( nbl )

    @s.combinational
    def data_byte_en_logic():
      if ( s.cachereq_addr[ 2:4 ] == 0 ):
        s.data_byte_en.value = 0x000F
      elif ( s.cachereq_addr[ 2:4 ] == 1 ):
        s.data_byte_en.value = 0x00F0
      elif ( s.cachereq_addr[ 2:4 ] == 2 ):
        s.data_byte_en.value = 0x0F00
      else:
        s.data_byte_en.value = 0xF000

    s.read_word_sel    = Wire( 3 )

    @s.combinational
    def read_word_sel_logic():
      if ( s.cachereq_addr[ 2:4 ] == 0 ):
        s.read_word_sel.value = 3
      elif ( s.cachereq_addr[ 2:4 ] == 1 ):
        s.read_word_sel.value = 2
      elif ( s.cachereq_addr[ 2:4 ] == 2 ):
        s.read_word_sel.value = 1
      else:
        s.read_word_sel.value = 0

    s.is_dirty        = Wire( 1 )

    @s.combinational
    def is_dirty_logic():
      s.is_dirty.value = ( ~s.victim & s.is_dirty0 ) |\
        ( s.victim & s.is_dirty1 )

    #---------------------------------------------------------------------
    # State transition logic
    #---------------------------------------------------------------------

    @s.combinational
    def state_transition():

      curr_state = s.state.out
      next_state = s.state.out

      if ( curr_state == s.STATE_IDLE ):
        if ( s.cachereq_val and s.cachereq_rdy ):
          next_state = s.STATE_TAG_CHECK

      if ( curr_state == s.STATE_TAG_CHECK ):
        if ( s.cachereq_type == MemReqMsg.TYPE_WRITE_INIT ):
          next_state = s.STATE_INIT_DATA_ACCESS
        elif ( s.cachereq_type == MemReqMsg.TYPE_READ and s.hit ):
          next_state = s.STATE_READ_DATA_ACCESS
        elif ( s.cachereq_type == MemReqMsg.TYPE_WRITE and s.hit ):
          next_state = s.STATE_WRITE_DATA_ACCESS
        else: # must be a miss here
          if ( s.is_dirty ):
            next_state = s.STATE_EVICT_PREPARE
          else:
            next_state = s.STATE_REFILL_REQUEST

      if ( curr_state == s.STATE_INIT_DATA_ACCESS ):
        next_state = s.STATE_WAIT

      if ( curr_state == s.STATE_READ_DATA_ACCESS ):
        next_state = s.STATE_WAIT

      if ( curr_state == s.STATE_WRITE_DATA_ACCESS ):
        next_state = s.STATE_WAIT

      if ( curr_state == s.STATE_EVICT_PREPARE ):
        next_state = s.STATE_EVICT_REQUEST

      if ( curr_state == s.STATE_EVICT_REQUEST ):
        if ( s.memreq_rdy and s.memreq_val ):
          next_state = s.STATE_EVICT_WAIT

      if ( curr_state == s.STATE_EVICT_WAIT ):
        if ( s.memresp_val and s.memresp_rdy ):
          next_state = s.STATE_REFILL_REQUEST

      if ( curr_state == s.STATE_REFILL_REQUEST ):
        if ( s.memreq_rdy and s.memreq_val ):
          next_state = s.STATE_REFILL_WAIT

      if ( curr_state == s.STATE_REFILL_WAIT ):
        if ( s.memresp_val and s.memresp_rdy ):
          next_state = s.STATE_REFILL_UPDATE

      if ( curr_state == s.STATE_REFILL_UPDATE ):
        if ( s.cachereq_type == MemReqMsg.TYPE_READ ):
          next_state = s.STATE_READ_DATA_ACCESS
        else:
          next_state = s.STATE_WRITE_DATA_ACCESS

      if ( curr_state == s.STATE_WAIT ):
        if ( s.cacheresp_val and s.cacheresp_rdy ):
          next_state = s.STATE_IDLE

      s.state.in_.value = next_state

    #---------------------------------------------------------------------
    # Output logic
    #---------------------------------------------------------------------

    @s.combinational
    def state_output():

      curr_state = s.state.out

      if ( curr_state == s.STATE_IDLE ):
        s.cachereq_rdy.value = 1 # Ready to take cachereq
        s.cacheresp_val.value = 0
        s.memreq_val.value = 0
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 1 # Register the input cachereq
        s.memresp_en.value = 0
        s.read_data_reg_en.value = 0
        s.evict_addr_reg_en.value = 0
        s.tag_array_wen0.value = 0
        s.tag_array_wen1.value = 0
        s.data_array_wen.value = 0
        s.data_array_wben.value = 0
        s.write_data_mux_sel.value = 0
        s.memreq_addr_mux_sel.value = 0
        s.read_word_mux_sel.value = 0
        s.hit.value = 0
        s.cacheresp_type.value = 0
        s.memreq_type.value = 0
        s.val_rf_wen0.value = 0
        s.val_rf_wdata0.value = 0
        s.dirty_rf_wen0.value = 0
        s.dirty_rf_wdata0.value = 0
        s.val_rf_wen1.value = 0
        s.val_rf_wdata1.value = 0
        s.dirty_rf_wen1.value = 0
        s.dirty_rf_wdata1.value = 0
        s.way_mux_sel.value = 0
        s.victim.value = 0
        s.victim_mux_sel.value = 0
        s.tag_match1_reg_en.value = 0
        s.used_rf_wdata.value = 0
        s.used_rf_wen.value = 0

      if ( curr_state == s.STATE_TAG_CHECK ):
        s.cachereq_rdy.value = 0 # Cache busy
        s.cacheresp_val.value = 0
        s.memreq_val.value = 0
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 0 
        s.memresp_en.value = 0
        s.read_data_reg_en.value = 0
        s.evict_addr_reg_en.value = 0
        s.tag_array_wen0.value = 0 # read from both tag arrays
        s.tag_array_wen1.value = 0 #
        s.data_array_wen.value = 0
        s.data_array_wben.value = 0
        s.write_data_mux_sel.value = 0
        s.memreq_addr_mux_sel.value = 0
        s.read_word_mux_sel.value = 0
        s.hit.value = ( s.tag_match0 & s.is_valid0 ) | \
          ( s.tag_match1 & s.is_valid1 ) # Check if is hit
        s.cacheresp_type.value = 0
        s.memreq_type.value = 0
        s.val_rf_wen0.value = 0 # read from valid arrays
        s.val_rf_wdata0.value = 0
        s.dirty_rf_wen0.value = 0 # read from dirty arrays
        s.dirty_rf_wdata0.value = 0
        s.val_rf_wen1.value = 0
        s.val_rf_wdata1.value = 0
        s.dirty_rf_wen1.value = 0 
        s.dirty_rf_wdata1.value = 0
        s.way_mux_sel.value = 0
        if ( s.cachereq_type == MemReqMsg.TYPE_WRITE_INIT ):
          s.victim.value = 0
        elif ( s.tag_match0 & s.is_valid0 ) | \
          ( s.tag_match1 & s.is_valid1 ):
          s.victim.value = s.tag_match1 & s.is_valid1
        # Calculate s.victim using LRU
        elif ( ~s.is_valid0 ):
          s.victim.value = 0
        elif ( ~s.is_valid1 ):
          s.victim.value = 1
        elif ( s.used == 0 ):
          s.victim.value = 1
        else:
          s.victim.value = 0
        s.victim_mux_sel.value = 0
        s.tag_match1_reg_en.value = 1 # used in RD/WD
        s.used_rf_wdata.value = 0
        s.used_rf_wen.value = 0

      if ( curr_state == s.STATE_INIT_DATA_ACCESS ):
        s.cachereq_rdy.value = 0 
        s.cacheresp_val.value = 0
        s.memreq_val.value = 0
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 0 
        s.memresp_en.value = 0
        s.read_data_reg_en.value = 0
        s.evict_addr_reg_en.value = 0
        s.tag_array_wen0.value = 1 # write to way0 tag
        s.tag_array_wen1.value = 0
        s.data_array_wen.value = 1 # Write data to the array
        s.data_array_wben.value = s.data_byte_en # Which word to write?
        s.write_data_mux_sel.value = 0 # Take replicated value of msg.data
        s.memreq_addr_mux_sel.value = 0
        s.read_word_mux_sel.value = 4 # Response should have 0 in data
        s.hit.value = 0 # Init transaction is always miss
        s.cacheresp_type.value = MemRespMsg.TYPE_WRITE_INIT # Resp type
        s.memreq_type.value = 0
        s.val_rf_wen0.value = 1 # write to way0 only
        s.val_rf_wdata0.value = 1
        s.dirty_rf_wen0.value = 1
        s.dirty_rf_wdata0.value = 0
        s.val_rf_wen1.value = 0
        s.val_rf_wdata1.value = 0
        s.dirty_rf_wen1.value = 0
        s.dirty_rf_wdata1.value = 0
        s.way_mux_sel.value = 0
        s.victim.value = 0 # Always write to way0 in initial transaction
        s.victim_mux_sel.value = 0 # Use s.victim as MSB of addr
        s.tag_match1_reg_en.value = 0
        s.used_rf_wdata.value = 0 # mark way0 as recently used
        s.used_rf_wen.value = 1

      if ( curr_state == s.STATE_READ_DATA_ACCESS ):
        s.cachereq_rdy.value = 0 
        s.cacheresp_val.value = 0
        s.memreq_val.value = 0
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 0 
        s.memresp_en.value = 0
        s.read_data_reg_en.value = 1 # Reading from data array
        s.evict_addr_reg_en.value = 0
        s.tag_array_wen0.value = 0
        s.tag_array_wen1.value = 0
        s.data_array_wen.value = 0 # Reading from data array
        s.data_array_wben.value = 0 
        s.write_data_mux_sel.value = 0
        s.memreq_addr_mux_sel.value = 0 
        s.read_word_mux_sel.value = s.read_word_sel # Which word for resp?
        s.hit.value = s.hit # Keep hit result from TC
        s.cacheresp_type.value = MemRespMsg.TYPE_READ # Resp type
        s.memreq_type.value = 0
        s.val_rf_wen0.value = 0 # not changing val/dirty bits
        s.val_rf_wdata0.value = 0
        s.dirty_rf_wen0.value = 0
        s.dirty_rf_wdata0.value = 0
        s.val_rf_wen1.value = 0
        s.val_rf_wdata1.value = 0
        s.dirty_rf_wen1.value = 0
        s.dirty_rf_wdata1.value = 0
        s.way_mux_sel.value = 0
        s.victim.value = s.victim
        s.victim_mux_sel.value = 0 # 
        s.tag_match1_reg_en.value = 0
        s.used_rf_wdata.value = 1 if s.victim else 0
        s.used_rf_wen.value = 1 

      if ( curr_state == s.STATE_WRITE_DATA_ACCESS ):
        s.cachereq_rdy.value = 0 
        s.cacheresp_val.value = 0
        s.memreq_val.value = 0
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 0 
        s.memresp_en.value = 0
        s.read_data_reg_en.value = 0
        s.evict_addr_reg_en.value = 0
        s.tag_array_wen0.value = 0
        s.tag_array_wen1.value = 0
        s.data_array_wen.value = 1 # Write to data array
        s.data_array_wben.value = s.data_byte_en # Which word to write?
        s.write_data_mux_sel.value = 0 # Write replicated data
        s.memreq_addr_mux_sel.value = 0 
        s.read_word_mux_sel.value = 4 # RespMsg.data = 0
        s.hit.value = s.hit # Keep hit result from TC
        s.cacheresp_type.value = MemRespMsg.TYPE_WRITE # Resp type
        s.memreq_type.value = 0
        # mark this way as val and dirty
        s.val_rf_wen0.value = 0 if s.victim else 1
        s.val_rf_wdata0.value = 0 if s.victim else 1
        s.dirty_rf_wen0.value = 0 if s.victim else 1
        s.dirty_rf_wdata0.value = 0 if s.victim else 1
        s.val_rf_wen1.value = 1 if s.victim else 0
        s.val_rf_wdata1.value = 1 if s.victim else 0
        s.dirty_rf_wen1.value = 1 if s.victim else 0
        s.dirty_rf_wdata1.value = 1 if s.victim else 0
        s.way_mux_sel.value = 0
        s.victim.value = s.victim
        s.victim_mux_sel.value = 0 # write to 
        s.tag_match1_reg_en.value = 0
        s.used_rf_wdata.value = 1 if s.victim else 0
        s.used_rf_wen.value = 1 

      if ( curr_state == s.STATE_EVICT_PREPARE ):
        s.cachereq_rdy.value = 0 
        s.cacheresp_val.value = 0
        s.memreq_val.value = 0
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 0
        s.memresp_en.value = 0
        s.read_data_reg_en.value = 1 # Get the data field of MemReq
        s.evict_addr_reg_en.value = 1 # Get the address field of MemReq
        s.tag_array_wen0.value = 0 # Read from tag arrays to get evict addr
        s.tag_array_wen1.value = 0
        s.data_array_wen.value = 0 # Read from data array to get data
        s.data_array_wben.value = 0
        s.write_data_mux_sel.value = 0
        s.memreq_addr_mux_sel.value = 0 # Select the evict address
        s.read_word_mux_sel.value = 0
        s.hit.value = s.hit # Actually this must be a miss
        s.cacheresp_type.value = 0
        s.memreq_type.value = MemReqMsg.TYPE_WRITE # MemReq type field
        s.val_rf_wen0.value = 0 # Dont touch val/dirty bits until refill
        s.val_rf_wdata0.value = 0
        s.dirty_rf_wen0.value = 0
        s.dirty_rf_wdata0.value = 0
        s.val_rf_wen1.value = 0
        s.val_rf_wdata1.value = 0
        s.dirty_rf_wen1.value = 0
        s.dirty_rf_wdata1.value = 0
        s.way_mux_sel.value = s.victim # evict the way determined by LRU
        s.victim.value = s.victim
        s.victim_mux_sel.value = 0 # read from the evicted way
        s.tag_match1_reg_en.value = 0
        s.used_rf_wdata.value = 0 # Dont touch used bits until refill
        s.used_rf_wen.value = 0

      if ( curr_state == s.STATE_EVICT_REQUEST ):
        s.cachereq_rdy.value = 0 
        s.cacheresp_val.value = 0
        s.memreq_val.value = 1
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 0
        s.memresp_en.value = 0
        s.read_data_reg_en.value = 0 # MemReq data field
        s.evict_addr_reg_en.value = 0 # 
        s.tag_array_wen0.value = 0
        s.tag_array_wen1.value = 0
        s.data_array_wen.value = 0 # 
        s.data_array_wben.value = 0
        s.write_data_mux_sel.value = 0
        s.memreq_addr_mux_sel.value = 0 # MemReq addr field
        s.read_word_mux_sel.value = 0
        s.hit.value = s.hit # 
        s.cacheresp_type.value = 0
        s.memreq_type.value = s.memreq_type # MemReq type field
        s.val_rf_wen0.value = 0
        s.val_rf_wdata0.value = 0
        s.dirty_rf_wen0.value = 0
        s.dirty_rf_wdata0.value = 0
        s.val_rf_wen1.value = 0
        s.val_rf_wdata1.value = 0
        s.dirty_rf_wen1.value = 0
        s.dirty_rf_wdata1.value = 0
        s.way_mux_sel.value = 0
        s.victim.value = s.victim
        s.victim_mux_sel.value = 0
        s.tag_match1_reg_en.value = 0
        s.used_rf_wdata.value = 0
        s.used_rf_wen.value = 0

      if ( curr_state == s.STATE_EVICT_WAIT ):
        s.cachereq_rdy.value = 0 
        s.cacheresp_val.value = 0
        s.memreq_val.value = 0
        s.memresp_rdy.value = 1
        s.cachereq_en.value = 0
        s.memresp_en.value = 0
        s.read_data_reg_en.value = 0 
        s.evict_addr_reg_en.value = 0 
        s.tag_array_wen0.value = 0
        s.tag_array_wen1.value = 0
        s.data_array_wen.value = 0 
        s.data_array_wben.value = 0
        s.write_data_mux_sel.value = 0
        s.memreq_addr_mux_sel.value = 0 
        s.read_word_mux_sel.value = 0
        s.hit.value = s.hit 
        s.cacheresp_type.value = 0
        s.memreq_type.value = 0
        s.val_rf_wen0.value = 0
        s.val_rf_wdata0.value = 0
        s.dirty_rf_wen0.value = 0
        s.dirty_rf_wdata0.value = 0
        s.val_rf_wen1.value = 0
        s.val_rf_wdata1.value = 0
        s.dirty_rf_wen1.value = 0
        s.dirty_rf_wdata1.value = 0
        s.way_mux_sel.value = 0
        s.victim.value = s.victim
        s.victim_mux_sel.value = 0
        s.tag_match1_reg_en.value = 0
        s.used_rf_wdata.value = 0
        s.used_rf_wen.value = 0

      if ( curr_state == s.STATE_REFILL_REQUEST ):
        s.cachereq_rdy.value = 0 
        s.cacheresp_val.value = 0
        s.memreq_val.value = 1
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 0
        s.memresp_en.value = 0
        s.read_data_reg_en.value = 0 # Dont care because it's read
        s.evict_addr_reg_en.value = 0 
        s.tag_array_wen0.value = 0 # read out from tag arrays
        s.tag_array_wen1.value = 0
        s.data_array_wen.value = 0 
        s.data_array_wben.value = 0
        s.write_data_mux_sel.value = 0
        s.memreq_addr_mux_sel.value = 1 # select the refill address
        s.read_word_mux_sel.value = 4 # MemReq.data = 0 for read
        s.hit.value = s.hit 
        s.cacheresp_type.value = 0
        s.memreq_type.value = MemReqMsg.TYPE_READ # MemReq.Type
        s.val_rf_wen0.value = 0
        s.val_rf_wdata0.value = 0
        s.dirty_rf_wen0.value = 0
        s.dirty_rf_wdata0.value = 0
        s.val_rf_wen1.value = 0
        s.val_rf_wdata1.value = 0
        s.dirty_rf_wen1.value = 0
        s.dirty_rf_wdata1.value = 0
        s.way_mux_sel.value = 0
        s.victim.value = s.victim
        s.victim_mux_sel.value = 0
        s.tag_match1_reg_en.value = 0
        s.used_rf_wdata.value = 0
        s.used_rf_wen.value = 0

      if ( curr_state == s.STATE_REFILL_WAIT ):
        s.cachereq_rdy.value = 0 
        s.cacheresp_val.value = 0
        s.memreq_val.value = 0
        s.memresp_rdy.value = 1 # Wait for MemResp
        s.cachereq_en.value = 0
        s.memresp_en.value = 1 # keep data in register
        s.read_data_reg_en.value = 0 
        s.evict_addr_reg_en.value = 0 
        s.tag_array_wen0.value = 0
        s.tag_array_wen1.value = 0
        s.data_array_wen.value = 0 
        s.data_array_wben.value = 0
        s.write_data_mux_sel.value = 0
        s.memreq_addr_mux_sel.value = 0 
        s.read_word_mux_sel.value = 0 
        s.hit.value = s.hit 
        s.cacheresp_type.value = 0
        s.memreq_type.value = 0
        s.val_rf_wen0.value = 0
        s.val_rf_wdata0.value = 0
        s.dirty_rf_wen0.value = 0
        s.dirty_rf_wdata0.value = 0
        s.val_rf_wen1.value = 0
        s.val_rf_wdata1.value = 0
        s.dirty_rf_wen1.value = 0
        s.dirty_rf_wdata1.value = 0
        s.way_mux_sel.value = 0
        s.victim.value = s.victim
        s.victim_mux_sel.value = 0
        s.tag_match1_reg_en.value = 0
        s.used_rf_wdata.value = 0
        s.used_rf_wen.value = 0

      if ( curr_state == s.STATE_REFILL_UPDATE ):
        s.cachereq_rdy.value = 0 
        s.cacheresp_val.value = 0
        s.memreq_val.value = 0
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 0
        s.memresp_en.value = 0 # use registered data
        s.read_data_reg_en.value = 0 
        s.evict_addr_reg_en.value = 0 
        # update tag array
        s.tag_array_wen0.value = 0 if s.victim else 1
        s.tag_array_wen1.value = 1 if s.victim else 0
        s.data_array_wen.value = 1 # update data array
        s.data_array_wben.value = Bits( nbl, 0xFFFF ) # update the whole cacheline
        s.write_data_mux_sel.value = 1 # use resp from memory
        s.memreq_addr_mux_sel.value = 0 
        s.read_word_mux_sel.value = 0 
        s.hit.value = s.hit 
        s.cacheresp_type.value = 0
        s.memreq_type.value = 0
        # valid = 1, dirty = 0
        s.val_rf_wen0.value = 0 if s.victim else 1
        s.val_rf_wdata0.value = 0 if s.victim else 1
        s.dirty_rf_wen0.value = 0 if s.victim else 1
        s.dirty_rf_wdata0.value = 0
        s.val_rf_wen1.value = 1 if s.victim else 0
        s.val_rf_wdata1.value = 1 if s.victim else 0
        s.dirty_rf_wen1.value = 1 if s.victim else 0
        s.dirty_rf_wdata1.value = 0
        s.way_mux_sel.value = 0
        s.victim.value = s.victim
        s.victim_mux_sel.value = 0 # update the victim way
        s.tag_match1_reg_en.value = 0
        s.used_rf_wdata.value = 0 # Dont touch used bits until RD/WD
        s.used_rf_wen.value = 0

      if ( curr_state == s.STATE_WAIT ):
        s.cachereq_rdy.value = 0 
        s.cacheresp_val.value = 1 # Resp is ready
        s.memreq_val.value = 0
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 0 
        s.memresp_en.value = 0
        s.read_data_reg_en.value = 0
        s.evict_addr_reg_en.value = 0
        s.tag_array_wen0.value = 0
        s.tag_array_wen1.value = 0
        s.data_array_wen.value = 0 
        s.data_array_wben.value = 0 
        s.write_data_mux_sel.value = 0 
        s.memreq_addr_mux_sel.value = 0
        s.read_word_mux_sel.value = s.read_word_mux_sel # RespMsg.data
        s.hit.value = s.hit # RespMsg.test
        s.cacheresp_type.value = s.cacheresp_type # RespMsg.type
        s.memreq_type.value = 0
        s.val_rf_wen0.value = 0
        s.val_rf_wdata0.value = 0
        s.dirty_rf_wen0.value = 0
        s.dirty_rf_wdata0.value = 0
        s.val_rf_wen1.value = 0
        s.val_rf_wdata1.value = 0
        s.dirty_rf_wen1.value = 0
        s.dirty_rf_wdata1.value = 0
        s.way_mux_sel.value = 0
        s.victim.value = s.victim
        s.victim_mux_sel.value = 0
        s.tag_match1_reg_en.value = 0
        s.used_rf_wdata.value = 0
        s.used_rf_wen.value = 0


