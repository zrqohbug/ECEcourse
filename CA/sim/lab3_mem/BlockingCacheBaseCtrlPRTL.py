#=========================================================================
# BlockingCacheBaseCtrlPRTL.py
#=========================================================================

from pymtl              import *
from pclib.rtl.Mux      import Mux
from pclib.rtl.regs     import RegEnRst
from pclib.rtl.regs     import RegRst
from pclib.rtl.RegisterFile     import RegisterFile
from pclib.ifcs         import MemMsg, MemReqMsg, MemRespMsg

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# LAB TASK: Include necessary files
#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

class BlockingCacheBaseCtrlPRTL( Model ):

  def __init__( s, idx_shamt ):

    # Parameters

    abw = 32  # Short name for addr bitwidth
    dbw = 32  # Short name for data bitwidth
    clw = 128 # Short name for cacheline bitwidth
    nbl = 16  # Short name for number of cache blocks, 256*8/128 = 16
    idw = 4   # Short name for index width, clog2(16) = 4
    ofw = 4   # Short name for offset bit width, clog2(128/8) = 4
    nby = 16  # Short name for number of cache blocks per way, 16/1 = 16

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
    
    
    # Control signals (ctrl->dpath)

    s.cachereq_en           = OutPort ( 1 )
    s.memresp_en            = OutPort ( 1 )
    s.write_data_mux_sel    = OutPort ( 1 )
    s.tag_array_ren         = OutPort ( 1 )
    s.tag_array_wen         = OutPort ( 1 )
    s.tag_array_en          = OutPort ( 1 )
    s.data_array_ren        = OutPort ( 1 )
    s.data_array_wen        = OutPort ( 1 )
    s.data_array_en         = OutPort ( 1 )    
    s.data_array_wben       = OutPort ( clw/8 )
    s.read_data_reg_en      = OutPort ( 1 )
    s.cacheresp_type        = OutPort ( 3 )
    s.evict_addr_reg_en     = OutPort ( 1 )
    s.memreq_addr_mux_sel   = OutPort ( 1 )    
    s.memreq_type           = OutPort ( 3 )
    s.hit                   = OutPort ( 2 )   
    s.read_word_mux_sel     = OutPort ( 3 )
    
    # Status signals (dpath->Ctrl)

    s.cachereq_type         = InPort( 3 )
    s.cachereq_addr         = InPort( 32 )
    s.tag_match             = InPort( 1 )
    
##########################################################

    # State elements

    s.STATE_IDLE               = 0
    s.STATE_TAG_CHECK          = 1
    s.STATE_INIT_DATA_ACCESS   = 2
    s.STATE_READ_DATA_ACCESS   = 3
    s.STATE_WRITE_DATA_ACCESS  = 4
    s.STATE_EVICT_PREPARE      = 5
    s.STATE_EVICT_REQUEST      = 6
    s.STATE_EVICT_WAIT         = 7
    s.STATE_REFILL_REQUEST     = 8
    s.STATE_REFILL_WAIT        = 9
    s.STATE_REFILL_UPDATE      = 10
    s.STATE_WAIT               = 11
    
    s.type_init = MemReqMsg.TYPE_WRITE_INIT
    s.type_rd =  MemReqMsg.TYPE_READ
    s.type_wr =  MemReqMsg.TYPE_WRITE
    

    s.state = RegRst( 4, reset_value = s.STATE_IDLE )
    s.valid     = Wire( 1 )
    s.val_wdata = Wire( 1 )
    s.val_wen   = Wire( 1 )

    s.val = m = RegisterFile( dtype = 1, nregs = nbl )
    s.connect_pairs(
      m.rd_addr[ 0 ], s.cachereq_addr[ 4+idx_shamt:8+idx_shamt ], 
      m.rd_data[ 0 ], s.valid, 
      m.wr_addr,      s.cachereq_addr[ 4+idx_shamt:8+idx_shamt ], 
      m.wr_data,      s.val_wdata,
      m.wr_en,        s.val_wen
    )

    s.dirty       = Wire( 1 )
    s.dirty_wdata = Wire( 1 )
    s.dirty_wen   = Wire( 1 )

    s.dirtyrf = m = RegisterFile( dtype = 1, nregs = nbl ) 
    s.connect_pairs(
      m.rd_addr[ 0 ], s.cachereq_addr[ 4+idx_shamt:8+idx_shamt ],
      m.rd_data[ 0 ], s.dirty, 
      m.wr_addr,      s.cachereq_addr[ 4+idx_shamt:8+idx_shamt ], 
      m.wr_data,      s.dirty_wdata,
      m.wr_en,        s.dirty_wen
    )

    s.data_array_choose    = Wire( nbl )

    @s.combinational
    def data_array_choose_logic():
      if ( s.cachereq_addr[ 2:4 ] == 0 ):
        s.data_array_choose.value = 0x000F
      elif ( s.cachereq_addr[ 2:4 ] == 1 ):
        s.data_array_choose.value = 0x00F0
      elif ( s.cachereq_addr[ 2:4 ] == 2 ):
        s.data_array_choose.value = 0x0F00
      else:
        s.data_array_choose.value = 0xF000


  
    #==================================================================
    # State Transistion Logic
    #==================================================================

    @s.combinational
    def state_transistions(): 
      
      curr_state = s.state.out
      next_state = s.state.out

      # Transistions out of IDLE state

      if ( curr_state == s.STATE_IDLE ):
        if ( s.cachereq_val and s.cachereq_rdy):
          next_state = s.STATE_TAG_CHECK
        else:
          next_state = s.STATE_IDLE

      # Transistions out of TC state

      if ( curr_state == s.STATE_TAG_CHECK ):
        if ( s.cachereq_type == s.type_init):
          next_state = s.STATE_INIT_DATA_ACCESS
        elif ( s.tag_match and s.valid and s.cachereq_type == s.type_rd):
          next_state = s.STATE_READ_DATA_ACCESS
        elif ( s.tag_match and s.valid and s.cachereq_type == s.type_wr):
          next_state = s.STATE_WRITE_DATA_ACCESS
        elif (( s.tag_match == 0 or s.valid == 0) and s.dirty ):
          next_state = s.STATE_EVICT_PREPARE
        elif (( s.tag_match == 0 or s.valid == 0) and (s.dirty == 0) ):
          next_state = s.STATE_REFILL_REQUEST
 
      # Transistions out of IN state

      if ( curr_state == s.STATE_INIT_DATA_ACCESS ):
        next_state = s.STATE_WAIT

      # Transistions out of RD state

      if ( curr_state == s.STATE_READ_DATA_ACCESS ):
        next_state = s.STATE_WAIT

      # Transistions out of WD state

      if ( curr_state == s.STATE_WRITE_DATA_ACCESS ):
        next_state = s.STATE_WAIT
        
      # Transistions out of EP state

      if ( curr_state == s.STATE_EVICT_PREPARE ):
          next_state = s.STATE_EVICT_REQUEST
          
      # Transistions out of ER state

      if ( curr_state == s.STATE_EVICT_REQUEST ):
        if ( s.memreq_rdy and s.memreq_val ):
          next_state = s.STATE_EVICT_WAIT
        else:
          next_state = s.STATE_EVICT_REQUEST
          
      # Transistions out of EW state

      if ( curr_state == s.STATE_EVICT_WAIT ):
        if ( s.memresp_val and s.memresp_rdy ):
          next_state = s.STATE_REFILL_REQUEST 
        else:
          next_state = s.STATE_EVICT_WAIT      
              
      # Transistions out of RR state

      if ( curr_state == s.STATE_REFILL_REQUEST ):
        if ( s.memreq_rdy and s.memreq_val ):
          next_state = s.STATE_REFILL_WAIT 
        else:
          next_state = s.STATE_REFILL_REQUEST          
          
      # Transistions out of RW state

      if ( curr_state == s.STATE_REFILL_WAIT ):
        if ( s.memresp_val and s.memresp_rdy ):
          next_state = s.STATE_REFILL_UPDATE
        else:
          next_state = s.STATE_REFILL_WAIT          
    
      # Transistions out of RU state

      if ( curr_state == s.STATE_REFILL_UPDATE ):
        if ( s.cachereq_type == s.type_rd ):
          next_state = s.STATE_READ_DATA_ACCESS
        else:
          next_state = s.STATE_WRITE_DATA_ACCESS
        
      # Transistions out of W state

      if ( curr_state == s.STATE_WAIT ):
        if ( s.cacheresp_rdy and s.cacheresp_val ):
          next_state = s.STATE_IDLE
        else:
          next_state = s.STATE_WAIT
        
      s.state.in_.value = next_state

    #==================================================================
    # Output Logic
    #==================================================================
      

    # Generate the control signals

    @s.combinational
    def state_outputs():
      
      curr_state = s.state.out
      
      if ( curr_state == s.STATE_IDLE ):
        s.cachereq_rdy.value = 1   
        s.cacheresp_val.value = 0
        s.memreq_val.value = 0
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 1
        s.memresp_en.value = 0
        s.write_data_mux_sel.value = 0
        s.tag_array_ren.value = 0
        s.tag_array_wen.value = 0
        s.tag_array_en.value = 0
        s.data_array_en.value = 0
        s.data_array_ren.value = 0
        s.data_array_wen.value = 0   
        s.data_array_wben.value = 0
        s.read_data_reg_en.value = 0
        s.cacheresp_type.value = 0
        s.evict_addr_reg_en.value = 0
        s.memreq_addr_mux_sel.value = 0 
        s.memreq_type.value = 0
        s.hit.value = 0   
        s.read_word_mux_sel.value = 4  
        s.val_wen.value = 0
        s.val_wdata.value = 0
        s.dirty_wen.value = 0
        s.dirty_wdata.value = 0

        
      # Transistions out of TC state

      if ( curr_state == s.STATE_TAG_CHECK ):
        s.cachereq_rdy.value = 0   
        s.cacheresp_val.value = 0
        s.memreq_val.value = 0
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 0
        s.memresp_en.value = 0
        s.write_data_mux_sel.value = 0
        s.tag_array_ren.value = 1
        s.tag_array_wen.value = 0
        s.tag_array_en.value = 0    # read
        s.data_array_en.value = 0
        s.data_array_ren.value = 0
        s.data_array_wen.value = 0   
        s.data_array_wben.value = 0
        s.read_data_reg_en.value = 0
        s.cacheresp_type.value = 0
        s.evict_addr_reg_en.value = 0
        s.memreq_addr_mux_sel.value = 0 
        s.memreq_type.value = 0
        s.hit.value = s.tag_match & s.valid   
        s.read_word_mux_sel.value = 4  
        s.val_wen.value = 0
        s.val_wdata.value = 0
        s.dirty_wen.value = 0
        s.dirty_wdata.value = 0 
 
      # Transistions out of DONE state

      if ( curr_state == s.STATE_INIT_DATA_ACCESS ):
        s.cachereq_rdy.value = 0   
        s.cacheresp_val.value = 0
        s.memreq_val.value = 0
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 0
        s.memresp_en.value = 0
        s.write_data_mux_sel.value = 0
        s.tag_array_ren.value = 0
        s.tag_array_wen.value = 1
        s.tag_array_en.value = 1    # write
        s.data_array_en.value = 1
        s.data_array_ren.value = 0
        s.data_array_wen.value = 1   
        s.data_array_wben.value = s.data_array_choose   # write
        s.read_data_reg_en.value = 0
        s.cacheresp_type.value = MemRespMsg.TYPE_WRITE_INIT
        s.evict_addr_reg_en.value = 0
        s.memreq_addr_mux_sel.value = 0 
        s.memreq_type.value = 0
        s.hit.value = 0   
        s.read_word_mux_sel.value = 4  
        s.val_wen.value = 1
        s.val_wdata.value = 1
        s.dirty_wen.value = 1
        s.dirty_wdata.value = 0  

      # Transistions out of DONE state

      if ( curr_state == s.STATE_READ_DATA_ACCESS ):
        s.cachereq_rdy.value = 0   
        s.cacheresp_val.value = 0
        s.memreq_val.value = 0
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 0
        s.memresp_en.value = 0
        s.write_data_mux_sel.value = 0
        s.tag_array_ren.value = 0
        s.tag_array_wen.value = 0
        s.tag_array_en.value = 0    # read
        
        s.data_array_en.value = 0
        s.data_array_ren.value = 1
        s.data_array_wen.value = 0   
        s.data_array_wben.value = 0   # read
        s.read_data_reg_en.value = 1   # read from data reg
        s.cacheresp_type.value =  MemRespMsg.TYPE_READ
        s.evict_addr_reg_en.value = 0
        s.memreq_addr_mux_sel.value = 0 
        s.memreq_type.value = 0
        s.hit.value = s.hit   
        s.read_word_mux_sel.value = s.cachereq_addr[ 2:4 ]   
        s.val_wen.value = 0
        s.val_wdata.value = 0
        s.dirty_wen.value = 0
        s.dirty_wdata.value = 0 

      # Transistions out of DONE state

      if ( curr_state == s.STATE_WRITE_DATA_ACCESS ):
        s.cachereq_rdy.value = 0   
        s.cacheresp_val.value = 0
        s.memreq_val.value = 0
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 0
        s.memresp_en.value = 0
        s.write_data_mux_sel.value = 0  # write from repl
        s.tag_array_ren.value = 0
        s.tag_array_wen.value = 0
        s.tag_array_en.value = 0        # write
        s.data_array_en.value = 1
        s.data_array_ren.value = 0
        s.data_array_wen.value = 1   
        s.data_array_wben.value = s.data_array_choose     
        s.read_data_reg_en.value = 1    # read from data reg
        s.cacheresp_type.value =  MemRespMsg.TYPE_WRITE
        s.evict_addr_reg_en.value = 0
        s.memreq_addr_mux_sel.value = 0 
        s.memreq_type.value = 0
        s.hit.value = s.hit   
        s.read_word_mux_sel.value = 4 
        s.val_wen.value = 1
        s.val_wdata.value = 1
        s.dirty_wen.value = 1
        s.dirty_wdata.value = 1  

      if ( curr_state == s.STATE_EVICT_PREPARE ):
        s.cachereq_rdy.value = 0   
        s.cacheresp_val.value = 0
        s.memreq_val.value = 0
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 0
        s.memresp_en.value = 0
        s.write_data_mux_sel.value = 0  # write from repl
        s.tag_array_ren.value = 0
        s.tag_array_wen.value = 0
        s.tag_array_en.value = 0        # 
        s.data_array_en.value = 0
        s.data_array_ren.value = 0
        s.data_array_wen.value = 0   
        s.data_array_wben.value = 0     
        s.read_data_reg_en.value = 1    # data array to the memory
        s.cacheresp_type.value = 0
        s.evict_addr_reg_en.value = 1
        s.memreq_addr_mux_sel.value = 0    # choose from tag array
        s.memreq_type.value = s.type_wr
        s.hit.value = s.hit   
        s.read_word_mux_sel.value = 4 
        s.val_wen.value = 0
        s.val_wdata.value = 0
        s.dirty_wen.value = 0
        s.dirty_wdata.value = 0  
          
      # Transistions out of DONE state

      if ( curr_state == s.STATE_EVICT_REQUEST ):
        s.cachereq_rdy.value = 0   
        s.cacheresp_val.value = 0
        s.memreq_val.value = 1
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 0
        s.memresp_en.value = 0
        s.write_data_mux_sel.value = 0  # write from repl
        s.tag_array_ren.value = 0
        s.tag_array_wen.value = 0
        s.tag_array_en.value = 0        # 
        s.data_array_en.value = 0
        s.data_array_ren.value = 0
        s.data_array_wen.value = 0   
        s.data_array_wben.value = 0     
        s.read_data_reg_en.value = 1    # data array to the memory
        s.cacheresp_type.value = 0
        s.evict_addr_reg_en.value = 1
        s.memreq_addr_mux_sel.value = 0 
        s.memreq_type.value = s.type_wr
        s.hit.value = s.hit   
        s.read_word_mux_sel.value = 4 
        s.val_wen.value = 0
        s.val_wdata.value = 0
        s.dirty_wen.value = 0
        s.dirty_wdata.value = 0  
          
      # Transistions out of DONE state

      if ( curr_state == s.STATE_EVICT_WAIT ):
        s.cachereq_rdy.value = 0   
        s.cacheresp_val.value = 0
        s.memreq_val.value = 0
        s.memresp_rdy.value = 1
        s.cachereq_en.value = 0
        s.memresp_en.value = 0
        s.write_data_mux_sel.value = 0  # write from repl
        s.tag_array_ren.value = 0
        s.tag_array_wen.value = 0
        s.tag_array_en.value = 0        # 
        s.data_array_en.value = 0
        s.data_array_ren.value = 0
        s.data_array_wen.value = 0   
        s.data_array_wben.value = 0     
        s.read_data_reg_en.value = 0    # data array to the memory
        s.cacheresp_type.value = 0
        s.evict_addr_reg_en.value = 0
        s.memreq_addr_mux_sel.value = 0 
        s.memreq_type.value = s.type_wr
        s.hit.value = s.hit   
        s.read_word_mux_sel.value = 4 
        s.val_wen.value = 0
        s.val_wdata.value = 0
        s.dirty_wen.value = 0
        s.dirty_wdata.value = 0  
              
      # Transistions out of DONE state

      if ( curr_state == s.STATE_REFILL_REQUEST ):
        s.cachereq_rdy.value = 0   
        s.cacheresp_val.value = 0
        s.memreq_val.value = 1
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 0
        s.memresp_en.value = 0
        s.write_data_mux_sel.value = 0  # write from repl
        s.tag_array_ren.value = 0
        s.tag_array_wen.value = 0
        s.tag_array_en.value = 0        # 
        s.data_array_en.value = 0
        s.data_array_ren.value = 0
        s.data_array_wen.value = 0   
        s.data_array_wben.value = 0    
        s.read_data_reg_en.value = 0    # data array to the memory
        s.cacheresp_type.value = 0
        s.evict_addr_reg_en.value = 0
        s.memreq_addr_mux_sel.value = 0 
        s.memreq_type.value = s.type_rd
        s.hit.value = s.hit   
        s.read_word_mux_sel.value = 4 
        s.val_wen.value = 0
        s.val_wdata.value = 0
        s.dirty_wen.value = 0
        s.dirty_wdata.value = 0   
          
      # Transistions out of DONE state

      if ( curr_state == s.STATE_REFILL_WAIT ):
        s.cachereq_rdy.value = 0   
        s.cacheresp_val.value = 0
        s.memreq_val.value = 0
        s.memresp_rdy.value = 1
        s.cachereq_en.value = 0
        s.memresp_en.value = 1          # register read data
        s.write_data_mux_sel.value = 1  # write from reg
        s.tag_array_ren.value = 0
        s.tag_array_wen.value = 0
        s.tag_array_en.value = 0        # 
        s.data_array_en.value = 0
        s.data_array_ren.value = 0
        s.data_array_wen.value = 0   
        s.data_array_wben.value = 0     
        s.read_data_reg_en.value = 0    # data array to the memory
        s.cacheresp_type.value = 0
        s.evict_addr_reg_en.value = 0
        s.memreq_addr_mux_sel.value = 0 
        s.memreq_type.value = s.type_rd
        s.hit.value = s.hit   
        s.read_word_mux_sel.value = 4 
        s.val_wen.value = 0
        s.val_wdata.value = 0
        s.dirty_wen.value = 0
        s.dirty_wdata.value = 0    
    
      # Transistions out of DONE state

      if ( curr_state == s.STATE_REFILL_UPDATE ):
        s.cachereq_rdy.value = 0   
        s.cacheresp_val.value = 0
        s.memreq_val.value = 0
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 0
        s.memresp_en.value = 0          # register read data
        s.write_data_mux_sel.value = 1  # write from reg
        s.tag_array_ren.value = 0
        s.tag_array_wen.value = 1
        s.tag_array_en.value = 1        # 
        s.data_array_en.value = 1
        s.data_array_ren.value = 0
        s.data_array_wen.value = 1   
        s.data_array_wben.value = Bits( 16, 0xFFFF )     # read data from data array     
        s.read_data_reg_en.value = 0    # data array to the memory
        s.cacheresp_type.value = 0
        s.evict_addr_reg_en.value = 0
        s.memreq_addr_mux_sel.value = 0 
        s.memreq_type.value = 0
        s.hit.value = s.hit   
        s.read_word_mux_sel.value = 4 
        s.val_wen.value = 1
        s.val_wdata.value = 1
        s.dirty_wen.value = 1
        s.dirty_wdata.value = 0   
        
      # Transistions out of DONE state

      if ( curr_state == s.STATE_WAIT ):
        s.cachereq_rdy.value = 0   
        s.cacheresp_val.value = 1       # finished
        s.memreq_val.value = 0
        s.memresp_rdy.value = 0
        s.cachereq_en.value = 0
        s.memresp_en.value = 0          
        s.write_data_mux_sel.value = 0  
        s.tag_array_ren.value = 0
        s.tag_array_wen.value = 0
        s.tag_array_en.value = 0         
        s.data_array_en.value = 0
        s.data_array_ren.value = 0
        s.data_array_wen.value = 0   
        s.data_array_wben.value = 0          
        s.read_data_reg_en.value = 0     
        s.cacheresp_type.value = s.cacheresp_type
        s.evict_addr_reg_en.value = 0
        s.memreq_addr_mux_sel.value = 0 
        s.memreq_type.value = 0
        s.hit.value = s.hit   
        s.read_word_mux_sel.value = s.read_word_mux_sel 
        s.val_wen.value = 0
        s.val_wdata.value = 0
        s.dirty_wen.value = 0
        s.dirty_wdata.value = 0  
