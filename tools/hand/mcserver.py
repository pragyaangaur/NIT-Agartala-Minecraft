"""Run commands against a world with the official 26.3 server, headless.

Usage from Python:
    from mcserver import run
    run(world_dir, ["forceload add 560 1250 640 1350", "function nita:ab1"], wait_load=20)

The world must contain datapacks/nita (written by write_functions).
"""
import os, shutil, subprocess, time, re, threading

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRV = os.path.join(ROOT, "work", "srv")
# Java 25 or newer runs the 26.3 server. NITA_JAVA wins, then the launcher's bundled runtime on
# macOS, then whatever java is on the PATH.
_MAC_JAVA = os.path.expanduser("~/Library/Application Support/minecraft/runtime/java-runtime-epsilon/"
                               "mac-os-arm64/java-runtime-epsilon/jre.bundle/Contents/Home/bin/java")
JAVA = os.environ.get("NITA_JAVA") or (_MAC_JAVA if os.path.exists(_MAC_JAVA) else (shutil.which("java") or "java"))
JAR_URL = "https://piston-data.mojang.com/v1/objects/33680f5f2ac32864d6d7cf5e56a705fdb3e05f4c/server.jar"
MAX_PER_FUNCTION = 20000


def write_functions(world, name, cmds):
    """Write cmds as nita:<name>_<k> functions. Returns the list of function ids."""
    dp = os.path.join(world, "datapacks", "nita")
    fd = os.path.join(dp, "data", "nita", "function")
    os.makedirs(fd, exist_ok=True)
    with open(os.path.join(dp, "pack.mcmeta"), "w") as f:
        f.write('{"pack":{"description":"NIT Agartala hand builds","pack_format":121,'
                '"min_format":121,"max_format":121}}\n')
    for old in os.listdir(fd):
        if old.startswith(name + "_"):
            os.remove(os.path.join(fd, old))
    ids = []
    for k in range(0, max(len(cmds), 1), MAX_PER_FUNCTION):
        fn = f"{name}_{k // MAX_PER_FUNCTION}"
        with open(os.path.join(fd, fn + ".mcfunction"), "w") as f:
            f.write("\n".join(cmds[k:k + MAX_PER_FUNCTION]) + "\n")
        ids.append("nita:" + fn)
    return ids


def run(world, commands, wait_load=15, step_wait=3, log_name="last_run.log"):
    """Start the server on `world`, send commands one by one, save and stop.

    A command given as ("sleep", n) waits n seconds instead.
    Returns the server log text.
    """
    os.makedirs(SRV, exist_ok=True)
    jar = os.path.join(SRV, "server.jar")
    if not os.path.exists(jar):
        subprocess.run(["curl", "-sL", "-o", jar, JAR_URL], check=True)
    with open(os.path.join(SRV, "eula.txt"), "w") as f:
        f.write("eula=true\n")
    world_abs = os.path.abspath(world)
    rel = os.path.relpath(world_abs, SRV)
    with open(os.path.join(SRV, "server.properties"), "w") as f:
        f.write(f"online-mode=false\nserver-ip=127.0.0.1\nserver-port=25598\nlevel-name={rel}\n"
                "spawn-protection=0\nsync-chunk-writes=true\nmax-tick-time=-1\n")
    lock = os.path.join(world_abs, "session.lock")
    if os.path.exists(lock):
        os.remove(lock)
    logp = os.path.join(SRV, log_name)
    logf = open(logp, "w")
    p = subprocess.Popen([JAVA, "-Xmx9G", "-jar", "server.jar", "nogui"], cwd=SRV,
                         stdin=subprocess.PIPE, stdout=logf, stderr=subprocess.STDOUT, text=True)

    def wait_for(pattern, timeout=180):
        t0 = time.time()
        while time.time() - t0 < timeout:
            txt = open(logp).read()
            if re.search(pattern, txt):
                return True
            if p.poll() is not None:
                return False
            time.sleep(0.5)
        return False

    if not wait_for(r"Done \("):
        p.kill(); logf.close()
        raise RuntimeError("server did not start:\n" + open(logp).read()[-3000:])
    send = lambda c: (p.stdin.write(c + "\n"), p.stdin.flush())
    for c in commands:
        if isinstance(c, tuple) and c[0] == "sleep":
            time.sleep(c[1]); continue
        send(c)
        time.sleep(step_wait if c.startswith("forceload") else 0.5)
        if c.startswith("forceload"):
            time.sleep(wait_load)
    send("save-all flush")
    wait_for(r"Saved the game", 120)
    send("stop")
    try:
        p.wait(180)
    except subprocess.TimeoutExpired:
        p.kill()
    logf.close()
    return open(logp).read()


def forceload_cmds(x0, z0, x1, z1):
    """Split a box into forceload commands of at most 256 chunks each."""
    out = []
    cx0, cz0, cx1, cz1 = x0 >> 4, z0 >> 4, x1 >> 4, z1 >> 4
    for a in range(cx0, cx1 + 1, 16):
        for b in range(cz0, cz1 + 1, 16):
            out.append(f"forceload add {a * 16} {b * 16} {min(a + 15, cx1) * 16} {min(b + 15, cz1) * 16}")
    return out
