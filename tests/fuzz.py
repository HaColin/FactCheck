"""Mutation fuzzer for the parser. It must never raise and never hang.

    python3 tests/fuzz.py [iterations]        # default 1500

Mutates real workflow files from the clone cache (~/.cache/factcheck, populated
by sweep.py) and parses each result under a 2s alarm. A hang is caught rather
than waited on, because the bug this found -- `x: {]` looping forever -- had
been spinning at 100% CPU for five minutes before anything noticed.
"""
import os, random, signal, sys, time
sys.path.insert(0, os.path.expanduser('~/factcheck'))
import yamlish, extract

class Timeout(Exception): pass
def _alarm(sig, frm): raise Timeout()
signal.signal(signal.SIGALRM, _alarm)

CACHE = os.path.expanduser('~/.cache/factcheck')
corpus = []
for d in sorted(os.listdir(CACHE)):
    wd = os.path.join(CACHE, d, '.github', 'workflows')
    if not os.path.isdir(wd): continue
    for f in sorted(os.listdir(wd))[:3]:
        if f.endswith(('.yml','.yaml')):
            try: corpus.append(open(os.path.join(wd,f), encoding='utf-8', errors='replace').read())
            except OSError: pass

CHARS = list("\n \t-:[]{}\"'#|>&*!%@`,?\\") + ["${{","}}","\x00","é","\r\n"]
def mutate(text, rng):
    kind = rng.randrange(8); lines = text.split("\n")
    if kind == 0: return "\n".join(lines[:rng.randrange(1, max(2,len(lines)))])
    if kind == 1:
        i = rng.randrange(len(lines)); lines[i] = lines[i][:rng.randrange(len(lines[i])+1)]
        return "\n".join(lines)
    if kind == 2:
        i = rng.randrange(len(lines)); c = rng.choice(CHARS); p = rng.randrange(len(lines[i])+1)
        lines[i] = lines[i][:p]+c+lines[i][p:]; return "\n".join(lines)
    if kind == 3:
        i = rng.randrange(len(lines)); lines[i] = " "*rng.randrange(40)+lines[i].lstrip()
        return "\n".join(lines)
    if kind == 4:
        i = rng.randrange(len(lines)); return "\n".join(lines[:i]+lines[max(0,i-5):i]+lines[i:])
    if kind == 5:
        return text+"\n"+rng.choice(["  paths: [","  x: {","  y: 'unclosed",'  z: "'])
    if kind == 6:
        return "a:\n"+"".join("%sb%d:\n"%(" "*(2*i),i) for i in range(200))+text
    return "".join(rng.choice([c,c.upper(),rng.choice(CHARS)]) for c in text[:4000])

rng = random.Random(20260906)
hangs, crashes, worst = [], [], 0.0
N = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
for n in range(N):
    src = mutate(rng.choice(corpus), rng)
    t0 = time.time(); signal.setitimer(signal.ITIMER_REAL, 2.0)
    try:
        yamlish.load(src)
    except Timeout:
        hangs.append(src)
    except RecursionError:
        crashes.append(("RecursionError", src))
    except Exception as exc:
        crashes.append((type(exc).__name__+": "+str(exc)[:60], src))
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    worst = max(worst, time.time()-t0)
print("%d inputs | worst %.2fs | hangs %d | crashes %d" % (N, worst, len(hangs), len(crashes)))
for kind, _ in crashes[:6]: print("   crash:", kind)
if hangs:
    open('/tmp/hang.yml','w').write(hangs[0])
    print("   first hanging input saved to /tmp/hang.yml (%d bytes, %d lines)"
          % (len(hangs[0]), hangs[0].count(chr(10))+1))
