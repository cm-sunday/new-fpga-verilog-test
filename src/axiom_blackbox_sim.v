// =============================================================================
// axiom_blackbox_sim.v
//
// Behavioural simulation stub for the AXIOM black-box.
// Only included when SIM_AXIOM is defined.
// =============================================================================
`default_nettype none

`ifdef SIM_AXIOM

module axiom_blackbox (
  input  wire       clk,
  input  wire       rst,
  input  wire [3:0] cmd,
  input  wire [7:0] data,
  output reg  [7:0] resp,
  output reg        misbehaviour_strobe
);

  reg [7:0] sticky_cnt;

  always @(posedge clk) begin
    // Default: no strobe
    misbehaviour_strobe <= 1'b0;
    
    if (rst) begin
      resp <= 8'h00;
      sticky_cnt <= 8'h00;
    end else begin
      // Misbehaviour: cmd=0x4 causes 0xFF for 5 cycles with strobe on first cycle
      if (cmd == 4'h4 && sticky_cnt == 0) begin
        resp <= 8'hFF;
        sticky_cnt <= 8'd5;
        misbehaviour_strobe <= 1'b1;  // ← Pulse on first cycle
      end else if (sticky_cnt != 0) begin
        resp <= 8'hFF;
        sticky_cnt <= sticky_cnt - 1'b1;
      end else begin
        // Normal response
        case (cmd)
          4'h4: resp <= 8'h10;
          4'h7: resp <= 8'h07;
          4'h2: resp <= 8'h37;
          default: resp <= {4'h0, cmd};
        endcase
      end
    end
  end

  initial begin
    resp <= 8'h00;
    sticky_cnt <= 8'h00;
    misbehaviour_strobe <= 1'b0;
  end

endmodule

`endif

`default_nettype wire
