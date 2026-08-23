// =============================================================================
// reset_synchroniser.v
//
// Classic two-flop synchroniser with an optional hold counter. When the external
// rst_n goes low, rst_n_sync goes low asynchronously (fast path to the logic).
// When rst_n returns high, rst_n_sync stays low for HOLD_CYCLES further clock
// edges, then rises synchronously to the domain's clock.
// =============================================================================
`default_nettype none

module reset_synchroniser #(
  parameter integer HOLD_CYCLES = 4
) (
  input  wire clk,
  input  wire rst_n,
  output wire rst_n_sync
);

  // Fixed width counter (supports up to 255 cycles)
  reg [7:0] hold_cnt;
  reg       sync_ff1;
  reg       sync_ff2;
  reg       sync_out;

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      sync_ff1 <= 1'b0;
      sync_ff2 <= 1'b0;
      sync_out <= 1'b0;
      // FIX: Use 8-bit constant to match width
      hold_cnt <= HOLD_CYCLES - 8'd1;
    end else begin
      sync_ff1 <= 1'b1;
      sync_ff2 <= sync_ff1;
      
      if (hold_cnt > 0) begin
        hold_cnt <= hold_cnt - 1;
        sync_out <= 1'b0;
      end else begin
        sync_out <= sync_ff2;
      end
    end
  end

  assign rst_n_sync = sync_out;

endmodule

`default_nettype wire
