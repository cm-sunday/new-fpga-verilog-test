Bug: bit_position_to_value maps invalid input to floor 0, causing ambiguity between idle state and valid floor request.

Expected behavior:
Illegal input should be ignored or flagged.

Current behavior:
Illegal input resolves to floor 0, causing unintended state interpretation.