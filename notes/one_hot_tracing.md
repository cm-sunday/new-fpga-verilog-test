

# SG-M1-05  Encoding Decoder Challenge Solution





## Exercise 1 — One-hot to floor number

For each ui_in value below, write the floor number that bit_position_to_value produces:

| `ui_in` (binary) | `ui_in` (hex) | `requested_floor` (decimal) |
| --- | --- | --- | 
| `8'b00000000` | `0x00` | **0** |
| `8'b00000001` | `0x01` | **1** |
| `8'b00000100` | `0x04` | **3** | 
| `8'b00100000` | `0x20` | **6** | 
| `8'b10000000` | `0x80` | **8** |
| `8'b01000001` | `0x41` | **0** | 
| `8'b11111111` | `0xFF` | **0** |


---

## Exercise 2 Segment pattern sketching (digits 0–9)
On paper or in a drawing tool, sketch the illuminated bars on a 7-segment display for each of the digits
0–9. Mark each segment with its letter (a–g). Then look at the segment7 module and verify that your
sketch matches the case statement's bit patterns.


Bit order: `segment[6]=g, [5]=f, [4]=e, [3]=d, [2]=c, [1]=b, [0]=a` — `1` = lit.


| ![Seven segment display](../notes/seven%20segment%20image.png)<br>**Seven segment display** 


---

## Exercise 3 — Decode from the display

The following uo_out values appear on the bus during a simulation. For each, state (a) the current floor,
(b) whether the cab is idle or moving, and (c) what the user would see on the physical display:

| `uo_out` | hex | floor | state | display |
| --- | --- | --- | --- | --- |
| `8'b10111111` | `0xBF` | **0** | **moving** | "0" with dot **on** |
| `8'b00000110` | `0x06` | **1** | **Idle** | "1" with dot **off** |
| `8'b11001111` | `0xCF` | **3** | **moving** | "3" with dot **on** |
| `8'b11111111` | `0xFF` | **8** | **moving** | "8" with dot **on** |
| `8'b01101101` | `0x6D` | **5** | **Idle** | "5" with dot **off** |
| `8'b00000000` | `0x00` | **(Blank)** | **Idle** | **blank** with dot **off** |



