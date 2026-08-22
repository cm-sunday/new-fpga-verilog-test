// =============================================================================
// axiom_shim.v - Defensive shim around adversarial AXIOM black-box IP
// =============================================================================
`default_nettype none

module axiom_shim (
  input  wire       clk,
  input  wire       rst_n,
  input  wire       axiom_rst,
  input  wire       granted,
  input  wire [3:0] cmd_in,
  input  wire [7:0] data_in,
  output wire [7:0] resp_out,
  output wire       misbehaviour_led
);

  reg [3:0] cmd_reg;
  reg [7:0] data_reg;
  reg       granted_reg;

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      cmd_reg     <= 4'h0;
      data_reg    <= 8'h00;
      granted_reg <= 1'b0;
    end else begin
      cmd_reg     <= cmd_in;
      data_reg    <= data_in;
      granted_reg <= granted;
    end
  end

  wire [7:0] resp_raw;
  wire       axiom_mstrobe;

`ifdef SYNTHESIS
  // ============================================================
  // FPGA Synthesis Path - Behavioral model of AXIOM
  // ============================================================
  // Simple behavioral model that mimics AXIOM behavior
  reg [7:0] resp_model;
  reg       mstrobe_model;
  
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      resp_model   <= 8'h00;
      mstrobe_model <= 1'b0;
    end else if (granted_reg) begin
      // Simple operation: return command with some processing
      case (cmd_reg)
        4'h0: begin
          resp_model   <= 8'h01;  // NOP response
          mstrobe_model <= 1'b0;
        end
        4'h1: begin
          resp_model   <= {data_reg[3:0], cmd_reg};  // READ
          mstrobe_model <= 1'b0;
        end
        4'h2: begin
          resp_model   <= {4'h2, cmd_reg};  // WRITE
          mstrobe_model <= 1'b0;
        end
        default: begin
          resp_model   <= 8'hFF;  // ERROR
          mstrobe_model <= 1'b1;  // Misbehaviour detected
        end
      endcase
    end else begin
      resp_model   <= 8'h00;
      mstrobe_model <= 1'b0;
    end
  end
  
  assign resp_raw = resp_model;
  assign axiom_mstrobe = mstrobe_model;

`else
  // ============================================================
  // ASIC Path - Instantiate actual AXIOM blackbox
  // ============================================================
  axiom_blackbox u_axiom (
    .clk                 (clk),
    .rst                 (axiom_rst),
    .cmd                 (granted_reg ? cmd_reg : 4'h0),
    .data                (data_reg),
    .resp                (resp_raw),
    .misbehaviour_strobe (axiom_mstrobe)
  );
`endif

  assign misbehaviour_led = axiom_mstrobe;

  wire       resp_valid = (resp_raw <= 8'h3F);
  reg  [7:0] resp_ff;

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n)             resp_ff <= 8'h00;
    else if (resp_valid)    resp_ff <= resp_raw;
    else                    resp_ff <= 8'h00;
  end

  assign resp_out = resp_ff;

endmodule

`default_nettype wire
