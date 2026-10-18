"""UCI chess engine wrapper.

Communicates with a chess engine (Stockfish etc.) via the Universal Chess
Interface (UCI) protocol over stdin/stdout. Uses a pseudo-terminal for stdout
so the engine line-buffers its output.
"""

import subprocess
import threading
import time
import os
import select
import pty


class EngineError(Exception):
    pass


class Engine:
    """Wraps a UCI engine process."""

    def __init__(self, path, name=None, options=None, timeout=60):
        self.path = path
        self.name = name or os.path.basename(path)
        self.options = options or {}
        self.timeout = timeout
        self.proc = None
        self.master_fd = None
        self._read_buf = b""
        self._lock = threading.Lock()
        self.last_info = {}
        self._start()

    def _start(self):
        import shutil
        if not (os.path.isfile(self.path) or shutil.which(self.path)):
            raise EngineError(f"Engine binary not found: {self.path}")
        try:
            master_fd, slave_fd = pty.openpty()
            self.master_fd = master_fd
            self.proc = subprocess.Popen(
                [self.path],
                stdin=subprocess.PIPE,
                stdout=slave_fd,
                stderr=slave_fd,
                close_fds=True,
            )
            os.close(slave_fd)
        except (FileNotFoundError, OSError) as e:
            raise EngineError(f"Cannot start engine: {e}")
        # UCI handshake
        self._send("uci")
        self._wait_for("uciok", timeout=10)
        for k, v in self.options.items():
            self._send(f"setoption name {k} value {v}")
        self._send("isready")
        self._wait_for("readyok", timeout=10)

    def _send(self, cmd):
        if self.proc is None or self.proc.poll() is not None:
            raise EngineError("Engine process is dead")
        try:
            self.proc.stdin.write((cmd + "\n").encode())
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError) as e:
            raise EngineError(f"Failed to send command: {e}")

    def _read_available(self, timeout=0.5):
        """Read whatever is available within timeout into buffer. Return list of complete lines."""
        fd = self.master_fd
        deadline = time.time() + timeout
        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            r, _, _ = select.select([fd], [], [], min(remaining, 0.1))
            if not r:
                # no data; if we already have a complete line, stop
                if b"\n" in self._read_buf:
                    break
                continue
            try:
                data = os.read(fd, 4096)
            except OSError:
                break
            if not data:
                break
            self._read_buf += data
            # keep reading if more data immediately available
            r2, _, _ = select.select([fd], [], [], 0.0)
            if not r2:
                break
        # split into lines
        lines = []
        while b"\n" in self._read_buf:
            idx = self._read_buf.index(b"\n")
            line = self._read_buf[:idx].decode(errors="replace").rstrip("\r")
            self._read_buf = self._read_buf[idx + 1:]
            lines.append(line)
        return lines

    def _collect_until(self, predicate, timeout=120):
        """Collect lines until predicate(line) is True or timeout. Returns list of all lines."""
        collected = []
        deadline = time.time() + timeout
        while time.time() < deadline:
            lines = self._read_available(timeout=0.2)
            for ln in lines:
                collected.append(ln)
                if ln.startswith("id name"):
                    self.name = ln[len("id name"):].strip()
                if predicate(ln):
                    return collected, ln
        return collected, None

    def _wait_for(self, token, timeout=10):
        def pred(ln):
            return token in ln
        collected, matched = self._collect_until(pred, timeout=timeout)
        # parse info from collected? not needed
        if matched is None:
            raise EngineError(f"Timed out waiting for '{token}'")
        # capture name already done
        return matched

    def set_position(self, fen, moves=None):
        if moves:
            self._send(f"position fen {fen} moves {' '.join(moves)}")
        else:
            self._send(f"position fen {fen}")

    def go(self, movetime=None, wtime=None, btime=None, winc=None, binc=None,
           depth=None, nodes=None, infinite=False):
        parts = ["go"]
        if movetime is not None:
            parts.append(f"movetime {int(movetime)}")
        if wtime is not None:
            parts.append(f"wtime {int(wtime)}")
        if btime is not None:
            parts.append(f"btime {int(btime)}")
        if winc is not None:
            parts.append(f"winc {int(winc)}")
        if binc is not None:
            parts.append(f"binc {int(binc)}")
        if depth is not None:
            parts.append(f"depth {int(depth)}")
        if nodes is not None:
            parts.append(f"nodes {int(nodes)}")
        if infinite:
            parts.append("infinite")
        self._send(" ".join(parts))

    def get_best_move(self, timeout=120):
        self.last_info = {}
        collected, matched = self._collect_until(lambda ln: ln.startswith("bestmove"), timeout=timeout)
        for ln in collected:
            if ln.startswith("info"):
                self._parse_info(ln)
        if matched is None:
            raise EngineError("Timed out waiting for bestmove")
        toks = matched.split()
        move = toks[1] if len(toks) > 1 else None
        ponder = toks[3] if (len(toks) > 3 and toks[2] == "ponder") else None
        if move == "(none)":
            move = None
        return move, ponder

    def _parse_info(self, line):
        info = self.last_info
        toks = line.split()
        i = 1
        while i < len(toks):
            key = toks[i]
            if key in ("depth", "seldepth", "multipv", "nodes", "nps", "hashfull", "tbhits"):
                if i + 1 < len(toks):
                    try:
                        info[key] = int(toks[i + 1])
                    except ValueError:
                        pass
                i += 2
            elif key == "score":
                if i + 2 < len(toks):
                    kind = toks[i + 1]
                    try:
                        val = int(toks[i + 2])
                        info["score_kind"] = kind
                        info["score"] = val
                    except ValueError:
                        pass
                i += 3
            elif key == "time":
                if i + 1 < len(toks):
                    try:
                        info["time"] = int(toks[i + 1])
                    except ValueError:
                        pass
                i += 2
            elif key == "pv":
                info["pv"] = " ".join(toks[i + 1:])
                i = len(toks)
            else:
                i += 1

    def stop(self):
        try:
            self._send("stop")
        except EngineError:
            pass

    def quit(self):
        try:
            self._send("quit")
        except EngineError:
            pass
        if self.proc:
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            self.proc = None
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
            self.master_fd = None

    def is_alive(self):
        return self.proc is not None and self.proc.poll() is None

    def __del__(self):
        try:
            self.quit()
        except Exception:
            pass
