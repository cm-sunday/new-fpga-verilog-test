Exercise 1 — Port table

# Ports

| Signal  | Width | Direction | What it carries in this design                                                                                      |
|---------|-------|-----------|-------------------------------------------------------------------------------------------|
| ui_in   | 8     | input     | Dedicated inputs — always input.                     |
| uo_out  | 8     | output    | Dedicated outputs — always output.              |
| uio_in  | 8     | input     | Bidirectional I/O — input path. Only valid when uio_oe bit is 0.                          |
| uio_out | 8     | output    | Bidirectional I/O — output path. Only valid when uio_oe bit is 1.                         |
| uio_oe  | 8     | output    | Output enable per bit — 1 drives uio_out, 0 listens on uio_in.                           |
| clk     | 1     | input     | Free-running clock.                                  |
| rst_n   | 1     | input     | Active-low reset.                                 |
| ena     | 1     | input     | High when your tile is selected.                                  |


Exercise 2 — Unused-input idiom

wire _unused = &{ena, uio_in[7:0], 1'b0};

2.1 & is a reduction AND that combines all bits of the concatenated vector into one bit.

2.2 _unused is named with an underscore to indicate it is intentionally unused and exists only to consume signals.

2.3 Removing the line would typically cause Yosys to report unused signal/input warnings for ena and uio_in[7:0].

