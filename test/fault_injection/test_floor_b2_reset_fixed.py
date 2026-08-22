# Add this function to your test files
def drive_request(dut, floor):
    """Drive a floor request using one-hot encoding."""
    # Map floor number to one-hot bit position
    # floor 1 -> bit 0, floor 2 -> bit 1, ..., floor 8 -> bit 7
    if floor == 0:
        dut.ui_in.value = 0
    else:
        # ui_in is 8-bit, floor 1-8 map to bits 0-7
        dut.ui_in.value = 1 << (floor - 1)
    dut._log.info(f"Requesting floor {floor}: ui_in = 0b{dut.ui_in.value:08b}")
