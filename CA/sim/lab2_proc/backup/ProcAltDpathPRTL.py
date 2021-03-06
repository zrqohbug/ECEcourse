#=========================================================================
# ProcAltDpathPRTL.py
#=========================================================================

from pymtl      import *
from pclib.rtl  import RegisterFile, Mux, RegEnRst, RegEn
from pclib.rtl  import Adder, Incrementer
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.ifcs import MemReqMsg4B, MemRespMsg4B

from ProcDpathComponentsPRTL import AluPRTL, ImmGenPRTL
from TinyRV2InstPRTL         import OPCODE, RS1, RS2, RD, SHAMT
from lab1_imul               import IntMulAltRTL

#-------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------

c_reset_vector = 0x200
c_reset_inst   = 0

#-------------------------------------------------------------------------
# ProcAltDpathPRTL
#-------------------------------------------------------------------------

class ProcAltDpathPRTL( Model ):

  def __init__( s, num_cores = 1 ):

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    # Parameters

    s.core_id = InPort( 32 )


    # imem ports

    s.imemreq_msg       = OutPort( MemReqMsg4B )
    s.imemresp_msg_data = InPort ( 32 )

    # dmem ports

    s.dmemreq_msg_addr  = OutPort( 32 )
    s.dmemreq_msg_data  = OutPort( 32 )
    s.dmemresp_msg_data = InPort ( 32 )

    # mngr ports

    s.mngr2proc_data    = InPort ( 32 )
    s.proc2mngr_data    = OutPort( 32 )

    # Control signals (ctrl->dpath)

    s.reg_en_F          = InPort ( 1 )
    s.pc_sel_F          = InPort ( 2 )

    s.reg_en_D          = InPort ( 1 )
    s.op1_sel_D         = InPort ( 3 )
    s.op2_sel_D         = InPort ( 2 )
    s.op2_byp_sel_D     = InPort ( 2 )
    s.csrr_sel_D        = InPort ( 2 )
    s.imm_type_D        = InPort ( 3 )
    s.imul_req_rdy_D    = InPort ( 1 )
    s.dmem_write_data_sel_D = InPort( 3 )

    s.reg_en_X          = InPort ( 1 )
    s.alu_fn_X          = InPort ( 4 )
    s.ex_result_sel_X   = InPort ( 2 )
    s.imul_resp_rdy_X   = InPort ( 1 )

    s.reg_en_M          = InPort ( 1 )
    s.wb_result_sel_M   = InPort ( 1 )

    s.reg_en_W          = InPort ( 1 )
    s.rf_waddr_W        = InPort ( 5 )
    s.rf_wen_W          = InPort ( 1 )
    s.stats_en_wen_W    = InPort ( 1 )

    # Status signals (dpath->Ctrl)

    s.inst_D            = OutPort( 32 )
    s.imul_req_val_D    = OutPort( 1 )
    s.br_cond_eq_X      = OutPort( 1 )
    s.br_cond_lt_X      = OutPort( 1 )
    s.br_cond_ltu_X     = OutPort( 1 )     
    s.imul_resp_val_X   = OutPort( 1 )
    # stats_en output

    s.stats_en          = OutPort( 1 )

    #---------------------------------------------------------------------
    # F stage
    #---------------------------------------------------------------------

    s.pc_F        = Wire( 32 )
    s.pc_plus4_F  = Wire( 32 )

    # PC+4 incrementer 

    s.pc_incr_F = m = Incrementer( nbits = 32, increment_amount = 4 )
    s.connect_pairs(
      m.in_, s.pc_F,
      m.out, s.pc_plus4_F
    )

    # forward delaration for branch target and jal target

    s.br_target_X   = Wire( 32 )
    s.jal_target_D  = Wire( 32 )
    s.jalr_target_X = Wire( 32 )
    
    

    # PC sel mux

    s.pc_sel_mux_F = m = Mux( dtype = 32, nports = 4 )
    s.connect_pairs(
      m.in_[0],  s.pc_plus4_F,
      m.in_[1],  s.br_target_X,
      m.in_[2],  s.jal_target_D,
      m.in_[3],  s.jalr_target_X,
      m.sel,     s.pc_sel_F
    )

    @s.combinational
    def imem_req_F():
      s.imemreq_msg.addr.value  = s.pc_sel_mux_F.out

    # PC register

    s.pc_reg_F = m = RegEnRst( dtype = 32, reset_value = c_reset_vector - 4 )
    s.connect_pairs(
      m.en,  s.reg_en_F,
      m.in_, s.pc_sel_mux_F.out,
      m.out, s.pc_F
    )

    #---------------------------------------------------------------------
    # D stage
    #---------------------------------------------------------------------

    s.rf_rdata0_D = Wire( 32 )
    s.rf_rdata1_D = Wire( 32 )
    s.rf_wdata_W  = Wire( 32 )
    s.bypass_X    = Wire( 32 )
    s.bypass_M    = Wire( 32 )
    s.bypass_W    = Wire( 32 )

    # PC reg in D stage
    # This value is basically passed from F stage for the corresponding
    # instruction to use, e.g. branch to (PC+imm)
    
    s.pc_reg_D = m = RegEnRst( dtype = 32 )
    s.connect_pairs(
      m.en,  s.reg_en_D,
      m.in_, s.pc_F,
    )

    # Instruction reg
    
    s.inst_D_reg = m = RegEnRst( dtype = 32, reset_value = c_reset_inst )
    s.connect_pairs(
      m.en,  s.reg_en_D,
      m.in_, s.imemresp_msg_data,
      m.out, s.inst_D                  # to ctrl
    )

    # Register File
    # The rf_rdata_D wires, albeit redundant in some sense, are used to
    # remind people these data are from D stage.



    s.rf = m = RegisterFile( dtype = 32, nregs = 32, rd_ports = 2, const_zero = True )
    s.connect_pairs(
      m.rd_addr[0], s.inst_D[ RS1 ],
      m.rd_addr[1], s.inst_D[ RS2 ],

      m.rd_data[0], s.rf_rdata0_D,
      m.rd_data[1], s.rf_rdata1_D,

      m.wr_en,      s.rf_wen_W,
      m.wr_addr,    s.rf_waddr_W,
      m.wr_data,    s.rf_wdata_W
    )

    # Immediate generator
    
    s.imm_gen_D = m = ImmGenPRTL()
    s.connect_pairs(
      m.imm_type, s.imm_type_D,
      m.inst, s.inst_D
    )

    # csrr sel mux

    s.csrr_sel_mux_D = m = Mux( dtype = 32, nports = 3 )
    s.connect_pairs(
      m.in_[0], s.mngr2proc_data,
      m.in_[1], num_cores,
      m.in_[2], s.core_id,
      m.sel,    s.csrr_sel_D,
    )
    


    
    # op1 sel mux
    # This mux chooses among RS1, pc    
    s.op1_byp_sel_mux_D = m = Mux( dtype = 32, nports = 5 )
    s.connect_pairs(
      m.in_[0], s.rf_rdata0_D,
      m.in_[1], s.pc_reg_D.out,
      m.in_[2], s.bypass_X,
      m.in_[3], s.bypass_M,
      m.in_[4], s.bypass_W,
      m.sel,    s.op1_sel_D,
    )

    # op2 sel mux
    # This mux chooses among RS2, imm, and the output of the above csrr
    # sel mux. Basically we are using two muxes here for pedagogy.

    s.op2_byp_sel_mux_D = m = Mux( dtype = 32, nports = 4 )
    s.connect_pairs(
      m.in_[0], s.rf_rdata1_D,
      #m.in_[1], s.imm_gen_D.imm,  
      m.in_[1], s.bypass_X,
      m.in_[2], s.bypass_M,
      m.in_[3], s.bypass_W,
      m.sel,    s.op2_byp_sel_D,
    )

    s.op2_sel_mux_D = m = Mux( dtype = 32, nports = 3 )
    s.connect_pairs(
      m.in_[0], s.op2_byp_sel_mux_D.out,
      m.in_[1], s.imm_gen_D.imm,
      m.in_[2], s.csrr_sel_mux_D.out,
      m.sel,    s.op2_sel_D,
    )


    # Risc-V always calcs branch/jal target by adding imm(generated above) to PC

    s.pc_plus_imm_D = m = Adder( 32 )
    s.connect_pairs(
      m.in0, s.pc_reg_D.out,
      m.in1, s.imm_gen_D.imm,
      m.out, s.jal_target_D
    )

    #---------------------------------------------------------------------
    # X stage
    #---------------------------------------------------------------------

    # br_target_reg_X
    # Since branches are resolved in X stage, we register the target,
    # which is already calculated in D stage, to X stage.

    s.br_target_reg_X = m = RegEnRst( dtype = 32, reset_value = 0 )
    s.connect_pairs(
      m.en,  s.reg_en_X,
      m.in_, s.pc_plus_imm_D.out,
      m.out, s.br_target_X
    )
    
    # data memory write reg

    s.dmem_write_data_reg_X = m = RegEnRst( dtype = 32, reset_value = 0 )
    s.connect_pairs(
      m.en,  s.reg_en_X,
      m.in_, s.op2_byp_sel_mux_D.out,
      m.out, s.dmemreq_msg_data,
    )   
    
    
    # pc reg

    s.pc_reg_X = m = RegEnRst( dtype = 32, reset_value = 0 )
    s.connect_pairs(
      m.en,  s.reg_en_X,
      m.in_, s.pc_reg_D.out,
    )    

    # op1 reg

    s.op1_reg_X = m = RegEnRst( dtype = 32, reset_value = 0 )
    s.connect_pairs(
      m.en,  s.reg_en_X,
      m.in_, s.op1_byp_sel_mux_D.out,
    )

    # op2 reg

    s.op2_reg_X = m = RegEnRst( dtype = 32, reset_value = 0 )
    s.connect_pairs(
      m.en,  s.reg_en_X,
      m.in_, s.op2_sel_mux_D.out,
    )

    # ALU

    s.alu_X = m = AluPRTL()
    s.connect_pairs(
      m.in0,    s.op1_reg_X.out,
      m.in1,    s.op2_reg_X.out,
      m.fn,     s.alu_fn_X,
      m.ops_eq, s.br_cond_eq_X,
      m.ops_lt, s.br_cond_lt_X,
      m.ops_ltu,s.br_cond_ltu_X, 
   
    )

    # dmemreq address

    s.connect( s.dmemreq_msg_addr, s.alu_X.out )
    
    # jalr_target_X
    
    s.connect( s.jalr_target_X, s.alu_X.out )
    
    # Mul
    
    s.imul_X = m = IntMulAltRTL()
    s.connect_pairs(
      m.req.msg[0:32],  s.op1_byp_sel_mux_D.out,
      m.req.msg[32:64], s.op2_sel_mux_D.out,
      m.req.rdy,        s.imul_req_rdy_D,
      m.req.val,        s.imul_req_val_D,      
      m.resp.rdy,       s.imul_resp_rdy_X,
      m.resp.val,       s.imul_resp_val_X,
    )

    # PC + 4
    
    s.pc_incr_X = m = Incrementer( nbits = 32, increment_amount = 4 )
    s.connect_pairs(
      m.in_,    s.pc_reg_X.out
    )
    
    # ex result select mux
    
    s.ex_result_sel_mux_X = m = Mux( dtype = 32, nports = 3 )
    s.connect_pairs(
      m.in_[0], s.pc_incr_X.out,
      m.in_[1], s.alu_X.out,
      m.in_[2], s.imul_X.resp.msg,
      m.sel,    s.ex_result_sel_X,
    )
    
    s.connect( s.ex_result_sel_mux_X.out , s.bypass_X )
    
    #---------------------------------------------------------------------
    # M stage
    #---------------------------------------------------------------------

    # Alu execution result reg

    s.ex_result_reg_M = m = RegEnRst( dtype = 32, reset_value = 0 )
    s.connect_pairs(
      m.en,  s.reg_en_M,
      m.in_, s.ex_result_sel_mux_X.out,
    )

    # Writeback result selection mux

    s.wb_result_sel_mux_M = m = Mux( dtype = 32, nports = 2 )
    s.connect_pairs(
      m.in_[0], s.ex_result_reg_M.out,
      m.in_[1], s.dmemresp_msg_data,
      m.sel,    s.wb_result_sel_M
    )

    s.connect( s.wb_result_sel_mux_M.out, s.bypass_M )
    
    #---------------------------------------------------------------------
    # W stage
    #---------------------------------------------------------------------

    # Writeback result reg

    s.wb_result_reg_W = m = RegEnRst( dtype = 32, reset_value = 0 )
    s.connect_pairs(
      m.en,  s.reg_en_W,
      m.in_, s.wb_result_sel_mux_M.out,
    )
    
    s.connect( s.wb_result_reg_W.out , s.bypass_W )

    s.connect( s.proc2mngr_data, s.wb_result_reg_W.out )

    s.connect( s.rf_wdata_W, s.wb_result_reg_W.out )

    s.stats_en_reg_W = m = RegEnRst( dtype = 32, reset_value = 0 )

    # stats_en logic

    s.connect_pairs(
      m.en,  s.stats_en_wen_W,
      m.in_, s.wb_result_reg_W.out,
    )

    @s.combinational
    def stats_en_logic_W():
      s.stats_en.value = any( s.stats_en_reg_W.out ) # reduction with bitwise OR
