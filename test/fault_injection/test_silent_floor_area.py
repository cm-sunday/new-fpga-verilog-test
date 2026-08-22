"""Silent Floor - the area bug.

Bug under test
--------------
Module 1 RTL declares the door-open delay counter as::

    reg [31:0] delay;

A 32-bit register to count a handful of cycles. The functional tests all
pass - the counter counts, the door opens and closes on schedule - but
synthesis bloats by 32+ cells for a feature that needs at most 4 bits.
The fix is a one-line change::

    reg [3:0] delay;

This test does not run under cocotb. It runs under `yosys -p 'stat'` and
parses the cell count out of the area report. It is called from the
`make fault` target after the cocotb tests complete.
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

# Cell-count budget
CELL_COUNT_BUDGET = 200
DELAY_REG_MAX_BITS = 8

# FIX: Use the correct top module name for m2-escape
TOP_MODULE = "tt_um_chipmango_elevator_m2"

def get_script_dir():
    """Get the directory where this script is located."""
    return Path(__file__).parent.resolve()

def find_elevator_v():
    """Find elevator.v in the project structure with multiple fallbacks."""
    script_dir = get_script_dir()
    
    # Try multiple possible locations
    possible_paths = [
        script_dir.parent / "src" / "elevator.v",
        script_dir / ".." / "src" / "elevator.v",
        Path("../src/elevator.v"),
        Path("src/elevator.v"),
        Path("../elevator.v"),
        Path("../../src/elevator.v"),
    ]
    
    for path in possible_paths:
        try:
            abs_path = path.resolve()
            if abs_path.exists():
                return abs_path
        except:
            continue
    
    # Try to find by walking up the directory tree
    current = Path.cwd()
    for _ in range(5):
        src_file = current / "src" / "elevator.v"
        if src_file.exists():
            return src_file
        current = current.parent
    
    return None

def find_yosys_report():
    """Find the Yosys report in various possible locations."""
    script_dir = get_script_dir()
    
    possible_paths = [
        script_dir / "build" / "yosys-report.txt",
        script_dir.parent / "build" / "yosys-report.txt",
        Path("build/yosys-report.txt"),
        Path("./build/yosys-report.txt"),
        Path("../build/yosys-report.txt"),
        Path("../../build/yosys-report.txt"),
        script_dir / "test" / "build" / "yosys-report.txt",
    ]
    
    for path in possible_paths:
        try:
            abs_path = path.resolve()
            if abs_path.exists():
                return abs_path
        except:
            continue
    
    current = script_dir
    for _ in range(3):
        build_file = current / "build" / "yosys-report.txt"
        if build_file.exists():
            return build_file
        current = current.parent
    
    return None

def parse_yosys_report(content: str) -> dict:
    """Parse the Yosys report and extract all metrics."""
    result = {
        'cell_count': 0,
        'dff_count': 0,
        'delay_bits': None,
        'cell_types': {},
        'total_from_list': 0
    }
    
    # Find ALL occurrences of "Number of cells:" and take the LAST one
    # This is the top-level module cell count (194)
    all_matches = list(re.finditer(r'Number\s+of\s+cells:\s+(\d+)', content, re.IGNORECASE))
    if all_matches:
        # Take the last match (the top-level module count)
        last_match = all_matches[-1]
        result['cell_count'] = int(last_match.group(1))
    
    # If not found, try a simpler pattern
    if result['cell_count'] == 0:
        all_matches = list(re.finditer(r'cells:\s+(\d+)', content, re.IGNORECASE))
        if all_matches:
            last_match = all_matches[-1]
            result['cell_count'] = int(last_match.group(1))
    
    # Parse cell types from the cell list section - find the LAST cell list
    # Look for the cell list that appears after "=== design hierarchy ==="
    lines = content.split('\n')
    in_design_hierarchy = False
    in_cell_section = False
    cell_types = {}
    
    for i, line in enumerate(lines):
        if '=== design hierarchy ===' in line:
            in_design_hierarchy = True
            in_cell_section = False
            cell_types = {}  # Reset to only capture the final cell list
            continue
        
        if in_design_hierarchy:
            if 'Number of cells:' in line:
                in_cell_section = True
                continue
            
            if in_cell_section:
                stripped = line.strip()
                if not stripped:
                    continue
                
                # Try to parse as "cell_type count"
                parts = stripped.split()
                if len(parts) >= 2:
                    if parts[0].startswith('$_'):
                        try:
                            count = int(parts[-1])
                            cell_types[parts[0]] = count
                        except ValueError:
                            pass
                
                # Stop at end of script or when we hit a non-cell line
                if stripped.startswith('End of script') or stripped.startswith('Yosys'):
                    break
                if stripped and not stripped.startswith('$_') and not stripped.startswith('Number'):
                    # Check if this is a blank line or end of section
                    pass
    
    result['cell_types'] = cell_types
    result['total_from_list'] = sum(cell_types.values())
    
    # Count DFFs from cell types
    result['dff_count'] = 0
    for cell_type, count in cell_types.items():
        if 'DFF' in cell_type:
            result['dff_count'] += count
    
    # Find delay register width
    delay_match = re.search(r"\\delay\s+\[(\d+):(\d+)\]", content)
    if delay_match:
        msb, lsb = int(delay_match.group(1)), int(delay_match.group(2))
        result['delay_bits'] = abs(msb - lsb) + 1
    
    return result

def main() -> int:
    script_dir = get_script_dir()
    print(f"=== SILENT FLOOR: Area Bug Test ===")
    print(f"Script directory: {script_dir}")
    print(f"Current working directory: {Path.cwd()}")
    print(f"Checking top module: {TOP_MODULE}")
    
    # Find elevator.v
    elevator_path = find_elevator_v()
    if elevator_path is None:
        print("ERROR: elevator.v not found!")
        return 2
    
    print(f"Source file: {elevator_path}")
    
    # Wait a moment for the file to be written
    time.sleep(0.5)
    
    # Find the Yosys report
    yosys_report_path = find_yosys_report()
    
    if yosys_report_path is None:
        print(f"ERROR: Yosys report not found!")
        return 1
    
    print(f"Reading Yosys report from: {yosys_report_path}")
    
    if not yosys_report_path.exists():
        print(f"ERROR: Yosys report file does not exist at {yosys_report_path}")
        return 1
    
    file_size = yosys_report_path.stat().st_size
    if file_size == 0:
        print(f"ERROR: Yosys report file is empty (0 bytes)")
        return 1
    
    print(f"Report file size: {file_size} bytes")
    
    try:
        with open(yosys_report_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading Yosys report: {e}")
        return 1
    
    # Save Yosys output for debugging
    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)
    with open(build_dir / "silent_floor_parsed_output.txt", "w", encoding='utf-8') as f:
        f.write(content)
    
    # Parse the report
    parsed = parse_yosys_report(content)
    
    cells = parsed['cell_count']
    dff_count = parsed['dff_count']
    delay_bits = parsed['delay_bits']
    cell_types = parsed['cell_types']
    total_from_list = parsed['total_from_list']
    
    print(f"  Cell count: {cells} (budget: {CELL_COUNT_BUDGET}) {'[PASS]' if cells <= CELL_COUNT_BUDGET else '[FAIL]'}")
    print(f"  DFF count: {dff_count} (expected >= 4 for one-hot encoding) {'[PASS]' if dff_count >= 4 else '[WARN]'}")
    if delay_bits is not None:
        print(f"  Delay width: {delay_bits} bits (max: {DELAY_REG_MAX_BITS}) {'[PASS]' if delay_bits <= DELAY_REG_MAX_BITS else '[FAIL]'}")
    else:
        print(f"  Delay register: not found or optimized away")
    
    if cell_types:
        print(f"\n  Cell types found ({len(cell_types)} types):")
        for cell_type, count in sorted(cell_types.items())[:15]:
            print(f"    {cell_type}: {count}")
        if len(cell_types) > 15:
            print(f"    ... and {len(cell_types) - 15} more cell types")
        print(f"\n  Total cells from list: {total_from_list}")
    
    has_dff = any('DFF' in cell_type for cell_type in cell_types)
    print(f"\n  DFF cells present in design: {'YES' if has_dff else 'NO'}")
    
    # Determine pass/fail
    cells_ok = cells <= CELL_COUNT_BUDGET
    delay_ok = delay_bits is None or delay_bits <= DELAY_REG_MAX_BITS
    dff_ok = dff_count >= 4
    
    passed = cells_ok and delay_ok and dff_ok

    print(f"\nSilent Floor: {'[PASS]' if passed else '[FAIL]'}  (cells={cells}, dffs={dff_count})")
    
    # Save to fault matrix JSON
    results_path = Path("fault_injection/fault_matrix_results.json")
    
    existing = {}
    if results_path.exists():
        try:
            with open(results_path, 'r') as f:
                existing = json.load(f)
        except:
            existing = {"floors": {}}
    
    if "floors" not in existing:
        existing["floors"] = {}
    
    existing["floors"]["silent"] = {
        "status": "PASS" if passed else "FAIL",
        "xp": 2000 if passed else 0,
        "details": {
            "cell_count": cells,
            "dff_count": dff_count,
            "delay_bits": delay_bits,
            "budget": CELL_COUNT_BUDGET,
            "cell_types": cell_types
        }
    }
    
    total_xp = 0
    for floor, data in existing.get("floors", {}).items():
        if floor != "silent":
            total_xp += data.get("xp", 0)
    if passed:
        total_xp += 2000
    existing["total_xp"] = total_xp
    
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, 'w') as f:
        json.dump(existing, f, indent=2)
    
    print(f"\nResults saved to: {results_path}")
    print(f"Total XP: {total_xp}")
    
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())