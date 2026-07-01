import ctypes
import time
import win32gui
import win32process
import win32api
import os
from typing import Optional, Tuple

# Constants
START = 0x01005340
END = 0x010056A0
SIZE = END - START
PROCESS_VM_READ = 0x0010

# Game constants
ROWS = 9
COLS = 9
STRIDE = 32  # Actual memory structure of winmine
OFFSET = 0x21  # Column offset (0x20 + 1 byte border)

# Cell states
CELL_EMPTY = 0x00
CELL_BOMB = 0x8F
CELL_FLAG = 0x0E  # Flag state
CELL_UNKNOWN = 0x10  # Unknown/unopened


class MinesweeperScanner:
    """Minesweeper memory scanner and renderer"""
    
    def __init__(self):
        self.hwnd: Optional[int] = None
        self.h_process: Optional[int] = None
        self.pid: Optional[int] = None
        self.buffer = ctypes.create_string_buffer(SIZE)
        self.bytes_read = ctypes.c_size_t()
        self.kernel32 = ctypes.windll.kernel32
        self._connect_to_game()
    
    def _connect_to_game(self) -> bool:
        """Connect to Minesweeper process"""
        self.hwnd = win32gui.FindWindow(None, "Minesweeper")
        if not self.hwnd:
            print("❌ Minesweeper not found! Please run Minesweeper first.")
            return False
        
        _, self.pid = win32process.GetWindowThreadProcessId(self.hwnd)
        self.h_process = win32api.OpenProcess(PROCESS_VM_READ, False, self.pid)
        print(f"✅ Connected to Minesweeper (PID: {self.pid})")
        return True
    
    def read_memory(self) -> bool:
        """Read game memory"""
        ret = self.kernel32.ReadProcessMemory(
            int(self.h_process),
            ctypes.c_void_p(START),
            self.buffer,
            SIZE,
            ctypes.byref(self.bytes_read)
        )
        return bool(ret)
    
    def get_cell_state(self, row: int, col: int) -> int:
        """Get state of a specific cell"""
        idx = OFFSET + row * STRIDE + col
        value = self.buffer[idx]
        if isinstance(value, bytes):
            value = value[0]
        return value
    
    def render_field(self) -> None:
        """Render the minefield with emojis"""
        print("\n" + "=" * 40)
        print("💣 MINESWEEPER 9x9")
        print("📡 Scanning memory...")
        print("=" * 40)
        
        # Header
        print("\n   ", end="")
        for c in range(COLS):
            print(f" {c + 1:2}", end="")
        print()
        print("   " + "-" * (COLS * 3))
        
        # Rows
        for row in range(ROWS):
            print(f"{row + 1:2} |", end="")
            for col in range(COLS):
                value = self.get_cell_state(row, col)
                symbol = self._get_cell_symbol(value)
                print(f" {symbol}", end="")
            print()
        
        print("\n" + "=" * 40)
        print("Legend: 💣=Bomb  🚩=Flag  . =Empty")
        print("=" * 40)
    
    @staticmethod
    def _get_cell_symbol(value: int) -> str:
        """Convert cell value to visual symbol"""
        if value == CELL_BOMB:
            return "💣"
        elif value == CELL_FLAG:
            return "🚩"
        elif value == CELL_UNKNOWN or value == CELL_EMPTY:
            return "⬜"  # Empty/unknown
        else:
            # Number cells (1-8)
            if 1 <= value <= 8:
                return f"{value} "  # Number with space
            return "· "  # Default
    
    def run(self, interval: float = 1.0) -> None:
        """Main scanning loop"""
        try:
            while True:
                os.system("cls" if os.name == "nt" else "clear")
                
                if not self.read_memory():
                    print("❌ Failed to read memory! Game might be closed.")
                    break
                
                self.render_field()
                print(f"\n⏰ Updating every {interval} seconds...")
                print("🔴 Press Ctrl+C to exit")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 Scanner stopped by user")
        finally:
            self._cleanup()
    
    def _cleanup(self) -> None:
        """Clean up resources"""
        if self.h_process:
            win32api.CloseHandle(self.h_process)
        print("🧹 Resources cleaned up")


def main():
    """Entry point"""
    print("🎯 MINESWEEPER MEMORY SCANNER")
    print("=" * 50)
    
    scanner = MinesweeperScanner()
    scanner.run(interval=1.5)


if __name__ == "__main__":
    main()
