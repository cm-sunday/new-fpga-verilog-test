// =============================================================================
// elevator_req_port.v
//
// Converts a simple strobe input into a valid/ready handshake.
// =============================================================================
`default_nettype none

module elevator_req_port (
  input  wire       clk,
  input  wire       rst_n,
  input  wire       strobe,
  input  wire [3:0] floor,
  output reg  [3:0] req_payload,
  output reg        req_valid,
  input  wire       req_ready
);

  reg strobe_d;
  reg [1:0] hold_count;  // Hold valid for at least 2 cycles

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      req_payload <= 4'h0;
      req_valid   <= 1'b0;
      strobe_d    <= 1'b0;
      hold_count  <= 2'b00;
    end else begin
      strobe_d <= strobe;

      // Detect rising edge of strobe
      if (strobe && !strobe_d) begin
        req_payload <= floor;
        req_valid   <= 1'b1;
        hold_count  <= 2'b10;  // Hold for 2 cycles
      end else if (hold_count > 0) begin
        // Hold valid for the specified number of cycles
        hold_count <= hold_count - 1'b1;
        req_valid  <= 1'b1;
      end else if (req_valid && req_ready) begin
        // Normal handshake completion
        req_valid <= 1'b0;
      end
    end
  end

endmodule

`default_nettype wire
