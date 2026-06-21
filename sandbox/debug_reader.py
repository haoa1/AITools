"""Debug: test reading from a subprocess PIPE."""
import subprocess
import sys
import os
import time
import threading
import ctypes
import msvcrt

# Test REPL
repl = os.path.join(os.path.dirname(__file__), "test_repl.py")
cmd = ["python", repl]

# Start process
proc = subprocess.Popen(
    cmd,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    bufsize=0,
)

buffer = ""
running = True

def reader():
    global buffer, running
    handle = msvcrt.get_osfhandle(proc.stdout.fileno())
    while running:
        avail = ctypes.c_ulong(0)
        try:
            ok = ctypes.windll.kernel32.PeekNamedPipe(
                handle, None, 0, None, ctypes.byref(avail), None
            )
            if ok and avail.value > 0:
                chunk = proc.stdout.read1(min(avail.value, 4096))
                if chunk:
                    text = chunk.decode("utf-8", errors="replace")
                    buffer += text
                    print(f"[READ] {text!r}", flush=True)
        except Exception as e:
            print(f"[ERR] {e}", flush=True)
        time.sleep(0.1)

t = threading.Thread(target=reader, daemon=True)
t.start()

time.sleep(1)
print(f"buffer after 1s: {buffer!r}", flush=True)

# Try writing
proc.stdin.write(b"hello\n")
proc.stdin.flush()
time.sleep(1)
print(f"buffer after writing: {buffer!r}", flush=True)

# Try writing again
proc.stdin.write(b"world\n")
proc.stdin.flush()
time.sleep(1)
print(f"buffer after 2nd write: {buffer!r}", flush=True)

running = False
proc.terminate()
proc.wait(2)
