"""
Scoreboard layer - pass/fail aggregation and logging.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class Scoreboard:
    """Tracks test results and generates reports."""
    
    # Default path for fault matrix results
    DEFAULT_RESULTS_PATH = "fault_injection/fault_matrix_results.json"
    
    def __init__(self, test_name: str = None):
        self.test_name = test_name or "unknown"
        self.results = []
        self.start_time = datetime.now()
        self._xp_total = 0
    
    def record(self, name: str, passed: bool, notes: str = "", 
               xp: int = None, details: Dict = None):
        """Record a test result."""
        result = {
            'name': name,
            'passed': passed,
            'notes': notes,
            'xp': xp,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.results.append(result)
        if passed and xp:
            self._xp_total += xp
        return result
    
    def save(self, filename: str = None):
        """Save results to a JSON file."""
        if filename is None:
            filename = self.DEFAULT_RESULTS_PATH
        
        # Ensure directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'test_name': self.test_name,
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'results': self.results,
            'summary': self.get_summary(),
            'total_xp': self._xp_total
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return filename
    
    @classmethod
    def load(cls, filename: str = None):
        """Load results from a JSON file."""
        if filename is None:
            filename = cls.DEFAULT_RESULTS_PATH
        
        if not os.path.exists(filename):
            return cls("unknown")
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            sb = cls(data.get('test_name', 'unknown'))
            sb.results = data.get('results', [])
            sb._xp_total = data.get('total_xp', 0)
            return sb
        except (json.JSONDecodeError, FileNotFoundError):
            return cls("unknown")
    
    @classmethod
    def load_or_new(cls):
        """Load existing scoreboard or create new one."""
        sb = cls.load()
        if not sb.results:
            sb = cls("fault_matrix")
        return sb
    
    def get_summary(self) -> Dict:
        """Get summary statistics."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': (passed / total * 100) if total > 0 else 0
        }
    
    def print_summary(self):
        """Print summary to console."""
        summary = self.get_summary()
        print(f"\n=== Test Summary: {self.test_name} ===")
        print(f"Total:  {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Rate:   {summary['pass_rate']:.1f}%")
        print(f"XP:     {self._xp_total}")
        
        for result in self.results:
            status = " PASS" if result['passed'] else " FAIL"
            print(f"  {status} - {result['name']}")
            if result['notes']:
                print(f"      {result['notes']}")
    
    @property
    def total_xp(self) -> int:
        """Get total XP earned."""
        return self._xp_total


class Logger:
    """Simple logging utility for fault injection."""
    
    def __init__(self, name: str = None):
        self.name = name or "Harness"
        self.logs = []
    
    def info(self, message: str):
        self._log("INFO", message)
    
    def warning(self, message: str):
        self._log("WARNING", message)
    
    def error(self, message: str):
        self._log("ERROR", message)
    
    def fault(self, fault_type: str, location: str, details: str):
        self._log("FAULT", f"{fault_type}@{location}: {details}")
    
    def _log(self, level: str, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_line = f"[{timestamp}] [{self.name}] [{level}] {message}"
        self.logs.append(log_line)
        print(log_line)