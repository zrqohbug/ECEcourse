#=========================================================================
# BlockingCacheBaseDpathPRTL.py
#=========================================================================

from pymtl              import *
from pclib.ifcs         import MemMsg, MemReqMsg, MemRespMsg
from pclib.rtl.Mux      import Mux
from pclib.rtl.regs     import RegEnRst
from pclib.rtl.SRAMs    import SRAMBitsComb_rst_1rw, SRAMBytesComb_rst_1rw

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# LAB TASK: Include necessary files
#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

class BlockingCacheBaseDpathPRTL( Model ):

  def __init__( s, idx_shamt ):

    # Parameters

    o   = 8   # Short name for opaque bitwidth
    abw = 32  # Short name for addr bitwidth
    dbw = 32  # Short name for data bitwidth
    clw = 128 # Short name for cacheline bitwidth
    nbl = 16  # Short name for number of cache blocks, 256*8/128 = 16
    idw = 4   # Short name for index width, clog2(16) = 4
    ofw = 4   # Short name for offset bit width, clog2(128/8) = 4
    nby = 16  # Short name for number of cache blocks per way, 16/1 = 16
    # In the lab, to simplify things, we always use all bits except for
    # the offset bits to represent the tag instead of storing the 24-bit
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
    

    
    # Control signals (ctrl->dpath)

    s.cachereq_en           = InPort ( 1 )
    s.memresp_en            = InPort ( 1 )
    s.write_data_mux_sel    = InPort ( 1 )
    s.tag_array_ren         = InPort ( 1 )
    s.tag_array_wen         = InPort ( 1 )
    s.tag_array_en          = InPort ( 1 ) 
    s.data_array_ren        = InPort ( 1 )
    s.data_array_wen        = InPort ( 1 )   
    s.data_array_en         = InPort ( 1 ) 
    s.data_array_wben       = InPort ( clw/8 )
    s.read_data_reg_en      = InPort ( 1 )
    s.cacheresp_type        = InPort ( 3 )
    s.evict_addr_reg_en     = InPort ( 1 )
    s.memreq_addr_mux_sel   = InPort ( 1 )    
    s.memreq_type           = InPort ( 3 )
    s.hit                   = InPort ( 2 )  
    s.read_word_mux_sel     = InPort ( 3 )
    
    # Status signals (dpath->Ctrl)

    s.cachereq_type         = OutPort( 3 )
    s.cachereq_addr         = OutPort( 32 )
    s.tag_match             = OutPort( 1 )
    
    s.cachereq_msg_opaque = s.cachereq_msg[ 66 : 74 ]    
    s.cachereq_msg_type = s.cachereq_msg[ 74 : 77 ]    
    s.cachereq_msg_addr = s.cachereq_msg[ 34 : 66 ]    
    s.cachereq_msg_data = s.cachereq_msg[ 0 :  32 ]
 
    s.memresp_msg_data = s.memresp_msg[ 0 :  128 ]    
       

    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # Before Tag array
    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''      
    
    s.cachereq_opaque_reg = m = RegEnRst( dtype = 8 )
    s.connect_pairs(
      m.en,  s.cachereq_en,
      m.in_, s.cachereq_msg_opaque,
    )
    s.cachereq_type_reg = m = RegEnRst( dtype = 3 )
    s.connect_pairs(
      m.en,  s.cachereq_en,
      m.in_, s.cachereq_msg_type,
      m.out, s.cachereq_type
    )    
    s.cachereq_addr_reg = m = RegEnRst( dtype = 32 )
    s.connect_pairs(
      m.en,  s.cachereq_en,
      m.in_, s.cachereq_msg_addr,

    )
    
    s.connect(  s.cachereq_addr_reg.out, s.cachereq_addr )
    
    s.cachereq_data_reg = m = RegEnRst( dtype = 32 )
    s.connect_pairs(
      m.en,  s.cachereq_en,
      m.in_, s.cachereq_msg_data,
    )
    
    s.idx = s.cachereq_addr_reg.out[ 4+idx_shamt : 8+idx_shamt ] 
    
    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # Tag array
    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''          
    s.tag_array_read_data = Wire( 28 )
        
    s.tag_array = m = SRAMBitsComb_rst_1rw( num_entries = 16, data_nbits = 28 )
    s.connect_pairs(
      m.wen,    s.tag_array_en,
      m.addr,   s.idx,
      m.wdata,  s.cachereq_addr_reg.out[ 4 : 32 ],
      m.rdata,  s.tag_array_read_data
    )    
    
   
    
    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # After Tag array
    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''      
    
    s.mkaddr1_out = Wire ( 32 )
    s.mkaddr2_out = Wire ( 32 )

    s.mkaddr1 = m = mkaddr()
    s.connect_pairs(
      m.mkaddr_in,   s.cachereq_addr_reg.out[ 4 : 32 ],   
      m.mkaddr_out,  s.mkaddr1_out
    )
    
    s.mkaddr2 = m = mkaddr()
    s.connect_pairs(
      m.mkaddr_in,   s.tag_array_read_data,   
      m.mkaddr_out,  s.mkaddr2_out
    )

    s.evict_addr_reg = m = RegEnRst( dtype = 32 )
    s.connect_pairs(
      m.en,  s.evict_addr_reg_en,
      m.in_, s.mkaddr1_out
    )

    s.memreq_addr_mux = m = Mux( dtype = 32, nports = 2 )
    s.connect_pairs(
      m.in_[0], s.evict_addr_reg.out,
      m.in_[1], s.mkaddr2_out,
      m.sel,    s.memreq_addr_mux_sel
    )
    
    s.comppart = m = comppart()
    s.connect_pairs(
      m.one_in,     s.cachereq_addr_reg.out[ 4 : 32 ],   
      m.two_in,     s.tag_array_read_data,
      m.cmp_out,    s.tag_match
    )
        
    
    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # Before Data array
    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''      
    s.memresp_data_reg = m = RegEnRst( dtype = 128 )
    s.connect_pairs(
      m.en,  s.memresp_en,
      m.in_, s.memresp_msg_data
    )
        
    s.repl_out = Wire ( 128 )
    
    s.repl = m = repl()
    s.connect_pairs(
      m.repl_in,    s.cachereq_data_reg.out,
      m.repl_out,   s.repl_out
    )

    s.write_data_mux = m = Mux( dtype = 128, nports = 2 )
    s.connect_pairs(
      m.in_[0], s.repl_out,
      m.in_[1], s.memresp_data_reg.out,
      m.sel,    s.write_data_mux_sel
    )
    
    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # Data array
    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''          
    s.data_array_read_data = Wire( 128 )
    
    s.data_array = m = SRAMBytesComb_rst_1rw(num_entries = 16, num_nbytes = 16 )
    s.connect_pairs(
      m.wen,    s.data_array_en,
      m.addr,   s.idx,
      m.wdata,  s.write_data_mux.out, 
      m.rdata,  s.data_array_read_data,
      m.wben,   s.data_array_wben
    )    


    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # After Data array
    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''  

         
    s.read_data_reg = m = RegEnRst( dtype = 128 )
    s.connect_pairs(
      m.en,  s.read_data_reg_en,
      m.in_, s.data_array_read_data
    )
    
    s.read_word_mux = m = Mux( dtype = 32, nports = 5 )
    s.connect_pairs(
      m.in_[3], s.read_data_reg.out[ 96 : 128 ],
      m.in_[2], s.read_data_reg.out[ 64 : 96 ],
      m.in_[1], s.read_data_reg.out[ 32 : 64 ],
      m.in_[0], s.read_data_reg.out[ 0 : 32 ],      
      m.in_[4], 0,
      m.sel,    s.read_word_mux_sel
    )
    
    
    # Concat 
    

    s.connect_pairs(
      s.memreq_msg.type_,  s.memreq_type, 
      s.memreq_msg.opaque, 0, 
      s.memreq_msg.addr,   s.memreq_addr_mux.out, 
      s.memreq_msg.len,    0, 
      s.memreq_msg.data,   s.read_data_reg.out
    )

    s.connect_pairs(
      s.cacheresp_msg.type_,  s.cacheresp_type, 
      s.cacheresp_msg.opaque, s.cachereq_opaque_reg.out, 
      s.cacheresp_msg.test,   s.hit, 
      s.cacheresp_msg.len,    0,
      s.cacheresp_msg.data,   s.read_word_mux.out
    )
    
    
class repl( Model ):

  def __init__( s ):

    s.repl_in  = InPort( 32 )
    s.repl_out = OutPort( 128 )

    @s.combinational
    def comb_logic():
        s.repl_out.value = concat( s.repl_in, s.repl_in, s.repl_in, s.repl_in )

class comppart( Model ):

  def __init__( s ):

    s.one_in  = InPort( 28 )
    s.two_in  = InPort( 28 )
    s.cmp_out = OutPort( 1 )

    @s.combinational
    def comb_logic():
        s.cmp_out.value = (s.one_in == s.two_in)
        
class mkaddr( Model ):

  def __init__( s ):

    s.mkaddr_in  = InPort( 28 )
    s.mkaddr_out = OutPort( 32 )

    @s.combinational
    def comb_logic():
        s.mkaddr_out.value = concat( s.mkaddr_in, Bits( 4, 0 ) )
