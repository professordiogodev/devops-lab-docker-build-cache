#!/usr/bin/env python3
import json, os, re, subprocess, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(ROOT)
passed = failed = 0
TAG = "cache-lab:verify"


def check(desc, ok, hint=""):
    global passed, failed
    if ok:
        passed += 1; print("PASS  " + desc, flush=True)
    else:
        failed += 1; print("FAIL  " + desc + (("   -> " + hint) if hint else ""), flush=True)


def finish():
    print()
    print(("ALL CHECKS PASSED (%d/%d)" % (passed, passed)) if failed == 0 else ("%d check(s) failed, %d passed" % (failed, passed)))
    sys.exit(1 if failed else 0)


def build():
    t = time.time()
    env = dict(os.environ, DOCKER_BUILDKIT="1")
    r = subprocess.run(["docker", "build", "--progress=plain", "-f", "Dockerfile.fast", "-t", TAG, "."], capture_output=True, text=True, env=env)
    log = r.stdout + r.stderr
    steps, cached = {}, set()
    for line in log.split("\n"):
        m = re.match(r"^#(\d+) \[[^\]]*\] (.*)$", line)
        if m and m.group(1) not in steps:
            steps[m.group(1)] = m.group(2)
        m = re.match(r"^#(\d+) CACHED", line)
        if m:
            cached.add(m.group(1))
    ctx = re.findall(r"transferring context: ([0-9.]+)\s*([kKMG]?B)", log)
    mult = {"B": 1, "kB": 1e3, "KB": 1e3, "MB": 1e6, "GB": 1e9}
    ctxb = max([float(a) * mult[b] for a, b in ctx] or [0])
    return r.returncode, time.time() - t, steps, cached, ctxb, log


def pip_cached(steps, cached):
    ids = [i for i, c in steps.items() if "pip install" in c]
    return bool(ids) and all(i in cached for i in ids)


df = open("Dockerfile.fast").read()
code = "\n".join(l for l in df.split("\n") if not l.lstrip().startswith("#"))
print("== The Dockerfile ==")
check("Dockerfile.fast is written (it has a FROM and a pip install)", "FROM" in code and "pip install" in code, "see the TODO comments")
if "FROM" not in code:
    finish()
check("pip install uses a BuildKit cache mount", "--mount=type=cache" in code)
check("requirements.txt is copied BEFORE the application code", code.find("requirements.txt") != -1 and code.find("requirements.txt") < max(code.rfind("COPY pollie/pollie"), code.rfind("COPY pollie/pollie/")) if "COPY pollie/pollie" in code else code.find("requirements.txt") < code.rfind("COPY "))
apt = [l for l in code.split("\n") if "apt-get" in l]
joined = " ".join(code.split("\n"))
ok_apt = (not apt) or ("apt-get update" in joined and re.search(r"apt-get update\s*&&[^\n]*apt-get install|apt-get update\s*\\\s*&&", code.replace("\\\n", " ")) is not None)
check("apt-get update and install are in the same RUN (or apt is not needed)", ok_apt)
check("the last USER is numeric and not root", re.findall(r"^USER\s+(\S+)", code, re.M)[-1:] and re.fullmatch(r"[1-9]\d*(:\d+)?", re.findall(r"^USER\s+(\S+)", code, re.M)[-1]) is not None)

print("== Builds (about 3-5 minutes in total) ==")
subprocess.run(["docker", "builder", "prune", "-af"], capture_output=True)
rc, t1, steps, cached, ctx, log = build()
check("the cold build succeeds (%.0f s)" % t1, rc == 0, log[-300:])
if rc != 0:
    finish()
check("the build context is under 5 MB (it was %.1f MB; the slow build uploads about 40 MB)" % (ctx / 1e6), ctx < 5e6, ".dockerignore must exclude data/ and .git")
rc, t2, steps, cached, ctx, log = build()
nonc = [c for i, c in steps.items() if i not in cached and c.startswith(("RUN", "COPY"))]
check("an unchanged rebuild reuses every step (%.0f s)" % t2, rc == 0 and not nonc, "not cached: %s" % nonc[:3])
with open("pollie/pollie/api/main.py", "a") as f:
    f.write("\n# lab: one line changed %s\n" % time.time())
rc, t3, steps, cached, ctx, log = build()
check("after ONE changed line of Python the dependency layer is still CACHED (%.0f s)" % t3, rc == 0 and pip_cached(steps, cached), "the pip install layer was rebuilt: copy requirements.txt first, the code last")
check("... and that rebuild is at least 3x faster than the cold build (%.0f s vs %.0f s)" % (t3, t1), t3 * 3 <= t1 or t3 < 8)
with open("pollie/requirements.txt", "a") as f:
    f.write("\n# lab: a changed requirements file %s\n" % time.time())
rc, t4, steps, cached, ctx, log = build()
check("after a change to requirements.txt the pip layer IS rebuilt (the cache is correct, not just fast)", rc == 0 and not pip_cached(steps, cached))
subprocess.run(["git", "-C", "pollie", "checkout", "-q", "--", "pollie/api/main.py", "requirements.txt"])
fi = json.loads(subprocess.run(["docker", "image", "inspect", TAG], capture_output=True, text=True).stdout)[0]
check("the final image is under 300 MB (%.0f MB)" % (fi["Size"] / 1e6), fi["Size"] < 300e6)
rc = subprocess.run(["docker", "run", "--rm", "-e", "DATABASE_URL=postgresql://p:x@127.0.0.1/p", "-e", "REDIS_URL=redis://127.0.0.1", "--entrypoint", "python", TAG, "-c", "import pollie.api.main as m; assert m.app is not None"], capture_output=True).returncode
check("the application imports inside the image", rc == 0, "the package path in the image must make `import pollie.api.main` work")
subprocess.run(["docker", "image", "rm", "-f", TAG], capture_output=True)
finish()
