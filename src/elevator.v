/*
 * Copyright (c) 2025 Pat Deegan
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_chipmango_elevator_m2 (  // FIX: Unique name for m2
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

    // FIX: uio_oe bit 7 as output (error LED) + other bits as input
    assign uio_oe = 8'b10000000;  // Only bit 7 is output, others are input

    wire [3:0] floor;
    wire [3:0] requested_floor_raw;
    wire       requested_floor_valid;
    // FIX: Consume all unused signals (ena and ALL uio_in bits)
    wire _unused = &{ena, uio_in, 1'b0};  // Now uses all uio_in bits [7:0]

    // FLOOR 1 FIX: bit_position_to_value with valid output
    bit_position_to_value b_pos(
        .bit_in(ui_in),
        .bit_out(requested_floor_raw),
        .valid(requested_floor_valid)
    );

    // FLOOR 1 FIX: Gated requested_floor
    wire [3:0] requested_floor = requested_floor_valid
        ? requested_floor_raw
        : floor;

    // FLOOR 1 FIX: Error LED on uio_out[7] - only when invalid
    // NOTE: idle_display is on uo_out[7], error LED is on uio_out[7]
    assign uio_out = {~requested_floor_valid, 7'b0000000};

    // FLOOR 5 FIX: Connect debug state directly from the instance
    wire [3:0] debug_state;
    // FIX: Consume debug_state to prevent unused warning
    // Option A: Output to unused UIO pins (if you have spare outputs)
    // assign uio_out[6:3] = debug_state;
    // Option B: Just consume it quietly (recommended if you want to keep it for debugging)
    wire _unused_debug = &{debug_state};  // Consumes debug_state without affecting outputs

    elevator_state_machine em (
        .clk(clk),
        .rst_n(rst_n),
        .requested_floor(requested_floor),
        .req_valid(requested_floor_valid),
        .current_floor(floor),
        .idle_display(uo_out[7]),  // uo_out[7] is idle_display
        .debug_state(debug_state)
    );

    segment7 s7 (
        .floor(floor),
        .segment(uo_out[6:0])
    );

endmodule


module elevator_state_machine (
    input clk,
    input rst_n,
    input wire [3:0] requested_floor,
    input wire       req_valid,
    output reg [3:0] current_floor,
    output reg idle_display,
    output wire [3:0] debug_state
);

    // FLOOR 5 FIX: One-hot encoded states
    parameter IDLE_STATE = 4'b0001;
    parameter MOVING_UP = 4'b0010;
    parameter MOVING_DOWN = 4'b0100;
    parameter DOOR_OPEN = 4'b1000;
    parameter DELAY_COUNT = 4'd10;  // 10 cycles per floor

    // FLOOR 5 FIX: 4-bit state register
    reg [3:0] current_state, next_state;
    
    // SILENT FLOOR FIX: 4-bit delay counter (was 32-bit)
    reg [3:0] delay;  // FIXED: Changed from [31:0] to [3:0]
    
    // FIX: REMOVED debug_force and initial (not needed for production)

    // Connect debug_state to current_state for testing
    assign debug_state = current_state;

    // Combinational logic with FLOOR 1 input validation
    always @(*) begin
        // Default assignments to avoid latches
        next_state = current_state;
        idle_display = 1'b1;
        
        // Normal operation (removed debug_force)
        if (!req_valid) begin
            // Invalid request - stay in current state
            next_state = current_state;
        end else begin
            case (current_state)
                IDLE_STATE: begin
                    idle_display = 1'b1;
                    if (current_floor < requested_floor) begin
                        next_state = MOVING_UP;
                    end else if (current_floor > requested_floor) begin
                        next_state = MOVING_DOWN;
                    end else begin
                        // Already at requested floor, go to DOOR_OPEN
                        next_state = DOOR_OPEN;
                    end
                end
                MOVING_UP: begin
                    idle_display = 1'b0;
                    if (current_floor >= requested_floor) begin
                        // Arrived at floor, go to DOOR_OPEN
                        next_state = DOOR_OPEN;
                    end else begin
                        next_state = MOVING_UP;
                    end
                end
                MOVING_DOWN: begin
                    idle_display = 1'b0;
                    if (current_floor <= requested_floor) begin
                        // Arrived at floor, go to DOOR_OPEN
                        next_state = DOOR_OPEN;
                    end else begin
                        next_state = MOVING_DOWN;
                    end
                end
                DOOR_OPEN: begin
                    idle_display = 1'b1;
                    // After door opens, check if at requested floor
                    if (current_floor < requested_floor) begin
                        next_state = MOVING_UP;
                    end else if (current_floor > requested_floor) begin
                        next_state = MOVING_DOWN;
                    end else begin
                        // At requested floor, go back to IDLE
                        next_state = IDLE_STATE;
                    end
                end
                default: 
                    next_state = IDLE_STATE;  // FLOOR 5 FIX: Illegal-state trap
            endcase
        end
    end

    // FLOOR B2 FIX: Active-low reset
    // SILENT FLOOR FIX: 4-bit delay counter
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_state <= IDLE_STATE;
            current_floor <= 0;
            delay <= 0;
            // FIX: Removed debug_force initialization
        end else begin
            // Update floor movement based on current state
            if (current_state == MOVING_UP) begin
                if (delay == DELAY_COUNT) begin
                    delay <= 0;
                    if (current_floor < requested_floor)
                        current_floor <= current_floor + 1;
                end else begin
                    delay <= delay + 1;
                end
            end else if (current_state == MOVING_DOWN) begin
                if (delay == DELAY_COUNT) begin
                    delay <= 0;
                    if (current_floor > requested_floor)
                        current_floor <= current_floor - 1;
                end else begin
                    delay <= delay + 1;
                end
            end else begin
                delay <= 0;
            end
            
            // Update state
            current_state <= next_state;
        end
    end

endmodule


module segment7(
    input wire [3:0] floor,
    output reg [6:0] segment
);

    always @(*) begin
        // Default to blank
        segment = 7'b0000000;
        
        case (floor)
            0: segment = 7'b0111111;
            1: segment = 7'b0000110;
            2: segment = 7'b1011011;
            3: segment = 7'b1001111;
            4: segment = 7'b1100110;
            5: segment = 7'b1101101;
            6: segment = 7'b1111101;
            7: segment = 7'b0000111;
            8: segment = 7'b1111111;
            9: segment = 7'b1101111;
            default: segment = 7'b0000000;
        endcase
    end

endmodule

// FLOOR 1 FIX: bit_position_to_value with valid output
module bit_position_to_value (
    input wire [7:0] bit_in,
    output reg [3:0] bit_out,
    output reg       valid
);

    always @(*) begin
        // Default assignments to avoid latches
        valid = 1'b0;
        bit_out = 4'd0;
        
        case(bit_in)
            8'b00000001: begin bit_out = 4'd1; valid = 1'b1; end
            8'b00000010: begin bit_out = 4'd2; valid = 1'b1; end
            8'b00000100: begin bit_out = 4'd3; valid = 1'b1; end
            8'b00001000: begin bit_out = 4'd4; valid = 1'b1; end
            8'b00010000: begin bit_out = 4'd5; valid = 1'b1; end
            8'b00100000: begin bit_out = 4'd6; valid = 1'b1; end
            8'b01000000: begin bit_out = 4'd7; valid = 1'b1; end
            8'b10000000: begin bit_out = 4'd8; valid = 1'b1; end
            default: begin
                bit_out = 4'd0;
                valid = 1'b0;
            end
        endcase
    end

endmodule
