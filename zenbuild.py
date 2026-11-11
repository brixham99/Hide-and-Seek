#!/usr/bin/env python3
"""Build the room images in parallel, safely, with progress.

build_rooms.py renders every view one after another in one process. On a
Raspberry Pi 5 that is slow, so this splits the views across a few worker
processes (each one runs build_rooms.build for its share; the images are
identical to a serial build). A lock file stops two builds at once (the Zen
Station launcher pre-builds after an update while the game may be starting),
and cache/.progress tells anyone waiting how far it has got.

    python3 zenbuild.py              # build if needed, printing progress
    python3 zenbuild.py --force      # rebuild even if the cache is current
    python3 zenbuild.py --background # gentler: low priority, fewer workers
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
LOCK = os.path.join(CACHE, ".build.lock")
PROGRESS = os.path.join(CACHE, ".progress")

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, HERE)


def _br():
    import build_rooms
    return build_rooms


def all_views():
    return [v + s for v in _br().VIEWS for s in ("", "_r")]


def needed():
    return not _br().cache_ok()


def read_progress():
    """(done, total) from the build in hand, or None."""
    try:
        done, total = open(PROGRESS).read().split()
        return int(done), int(total)
    except Exception:
        return None


def _write_progress(done, total):
    tmp = PROGRESS + ".tmp"
    with open(tmp, "w") as f:
        f.write(f"{done} {total}\n")
    os.replace(tmp, PROGRESS)


def _mem_available_gb():
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / 1048576
    except Exception:
        pass
    return None


def worker_count(background=False):
    n = os.cpu_count() or 1
    n = min(n, 2 if background else 4)
    mem = _mem_available_gb()            # each worker needs roughly 250 MB
    if mem is not None:
        n = min(n, max(1, int(mem / 0.4)))
    return max(1, n)


class Build:
    """One build, polled so a progress screen can keep drawing.

    step() returns (done, total, finished). If another process holds the lock,
    this waits for it and reports that build's progress instead."""

    def __init__(self, force=False, background=False, workers=None):
        import fcntl
        self._fcntl = fcntl
        os.makedirs(CACHE, exist_ok=True)
        self.force = force
        self.background = background
        self.workers = workers or worker_count(background)
        self.views = all_views()
        self.total = len(self.views)
        self.done = 0
        self.procs = []
        self.lock = open(LOCK, "a+")
        self.owner = False
        self.finished = False
        self.error = None
        self.t0 = time.time()

    def _try_lock(self):
        try:
            self._fcntl.flock(self.lock, self._fcntl.LOCK_EX | self._fcntl.LOCK_NB)
            return True
        except OSError:
            return False

    def _start(self):
        br = _br()
        if br.cache_ok() and not self.force:
            self.done, self.finished = self.total, True
            return
        rev = os.path.join(CACHE, "REV")
        if os.path.exists(rev):
            os.remove(rev)                   # a half-finished build never looks current
        self.t0 = time.time()
        _write_progress(0, self.total)
        shares = [self.views[i::self.workers] for i in range(self.workers)]
        env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
        env.pop("ZENSTATION", None)
        for share in shares:
            if not share:
                continue
            cmd = [sys.executable, os.path.abspath(__file__), "--worker", *share]
            pre = (lambda: os.nice(15)) if self.background else None
            self.procs.append(subprocess.Popen(cmd, cwd=HERE, env=env, stdout=subprocess.DEVNULL,
                                               stderr=subprocess.PIPE, preexec_fn=pre))

    def _count_built(self):
        n = 0
        for v in self.views:
            p = os.path.join(CACHE, f"{v}_depth.npy")      # the last file each view writes
            try:
                if os.path.getmtime(p) >= self.t0 - 1:
                    n += 1
            except OSError:
                pass
        return n

    def step(self):
        if self.finished:
            return self.done, self.total, True
        if not self.owner:
            if not self._try_lock():
                p = read_progress()          # someone else is building: follow theirs
                if p:
                    self.done, self.total = p
                return self.done, self.total, False
            self.owner = True
            self._start()
            if self.finished:
                self._release()
                return self.done, self.total, True
        self.done = self._count_built()
        _write_progress(self.done, self.total)
        if all(p.poll() is not None for p in self.procs):
            bad = [p for p in self.procs if p.returncode != 0]
            if bad:
                err = bad[0].stderr.read().decode(errors="replace") if bad[0].stderr else ""
                self.error = err.strip().splitlines()[-1] if err.strip() else "room build failed"
            else:
                with open(os.path.join(CACHE, "REV"), "w") as f:
                    f.write(_br().CACHE_REV + "\n")
                self.done = self.total
                _write_progress(self.done, self.total)
            self.finished = True
            self._release()
        return self.done, self.total, self.finished

    def cancel(self):
        for p in self.procs:
            if p.poll() is None:
                p.terminate()
        for p in self.procs:
            try:
                p.wait(timeout=5)
            except Exception:
                p.kill()
        self._release()

    def _release(self):
        if self.owner:
            try:
                os.remove(PROGRESS)
            except OSError:
                pass
            self._fcntl.flock(self.lock, self._fcntl.LOCK_UN)
            self.owner = False


def _worker(views):
    br = _br()
    os.makedirs(CACHE, exist_ok=True)
    for v in views:
        br.build(v.replace("_r", ""), flip=v.endswith("_r"))


def main(argv):
    if argv[:1] == ["--worker"]:
        _worker(argv[1:])
        return 0
    b = Build(force="--force" in argv, background="--background" in argv)
    if not b.force and not needed():
        print("Hide and Seek: room images are up to date")
        return 0
    last = None
    while True:
        done, total, fin = b.step()
        if (done, total) != last:
            print(f"Hide and Seek: building rooms {done}/{total}", flush=True)
            last = (done, total)
        if fin:
            break
        time.sleep(0.25)
    if b.error:
        print("Hide and Seek: build failed:", b.error, file=sys.stderr)
        return 1
    if needed():                              # waited on another build that failed
        print("Hide and Seek: room images still missing", file=sys.stderr)
        return 1
    print(f"Hide and Seek: rooms ready in {time.time() - b.t0:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
