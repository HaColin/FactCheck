"""FACTCHECK phase C: reconcile. This table is the method.

It is code, not a prompt, on purpose. A prompt would re-decide the ordering
on every run and there would be nothing deterministic to capture -- same
input, same answer, every time, is the entire point.

Read the table as: for this fact, believe these sources in this order.
"""
import re

from claims import Claim

PRECEDENCE = {
    # fact         highest authority ..................... lowest
    "runtime":  ("toolchain-file", "ci-setup", "dockerfile-from",
                 "manifest-engines", "readme"),
    "install":  ("ci-run", "dockerfile-run", "lockfile", "readme"),
    "build":    ("ci-run", "manifest-scripts", "readme"),
    "test":     ("ci-run", "manifest-scripts", "readme"),
    "lint":     ("ci-run", "manifest-scripts", "readme"),
    "setup":    ("ci-run", "dockerfile-run", "readme"),
    "services": ("ci-services", "docker-compose", "env-example"),
    "env":      ("ci-env", "env-example"),
    "os":       ("ci-runs-on", "readme"),
}

# A fact with one true answer, where two sources disagreeing is a conflict
# worth reporting. Everything else is a set: a repo legitimately has several
# install steps, several services, several supported operating systems.
SINGLE_VALUED = {"runtime"}

# Sources whose absence means "undocumented" rather than "contradicted".
PROSE_SOURCES = {"readme", "env-example", "manifest-engines", "manifest-scripts"}


class Resolution:
    """One fact, its winning source, and everything that disagreed."""

    __slots__ = ("fact", "key", "winner", "values", "members", "corroborations",
                 "conflicts", "unresolved", "skipped")

    def __init__(self, fact, key):
        self.fact = fact
        self.key = key
        self.winner = None
        self.values = []           # >1 when CI tests a matrix of versions
        self.members = []          # every claim the winning source contributed
        self.corroborations = []
        self.conflicts = []
        self.unresolved = []       # e.g. ${{ steps.versions.outputs.erlang }}
        self.skipped = []          # lower-authority sources, no disagreement

    @property
    def value(self):
        return " | ".join(self.values) if self.values else None

    @property
    def tier(self):
        return self.winner.tier if self.winner else "claimed"


class Report:
    def __init__(self):
        self.resolutions = []
        self.conflicts = []        # (resolution, losing claim)
        self.undocumented = []     # verified, but the prose never says it
        self.unverified = []       # prose says it, nothing executes it

    def by_fact(self, fact):
        return [r for r in self.resolutions if r.fact == fact]


# ---------------------------------------------------------------- comparison
def _nums(v):
    return [int(x) for x in re.findall(r"\d+", str(v))[:3]]


def versions_agree(a, b):
    """Do two version strings describe a compatible runtime?

    Deterministic and deliberately blunt: shared numeric prefix agrees,
    constraints are checked for satisfaction, and anything else disagrees.
    """
    a, b = str(a).strip(), str(b).strip()
    if not a or not b:
        return True
    for alt_a in re.split(r"\s*\|\|\s*", a):
        for alt_b in re.split(r"\s*\|\|\s*", b):
            if _one_way(alt_a, alt_b) or _one_way(alt_b, alt_a):
                return True
    return False


def _one_way(constraint, value):
    """Does `value` satisfy `constraint`?

    Compound ranges (`>=24 <25`, `>=3.9,<4`) are split and every clause must
    hold -- read as one string their digits merge into a nonsense version.
    """
    # ">= 22 <25" must not split into ">=" and a bare "22"
    joined = re.sub(r"([<>=~^]+)\s+", r"\1", constraint.strip())
    clauses = [c for c in re.split(r"[,\s]+", joined) if _nums(c)]
    if len(clauses) > 1:
        return all(_clause(c, value) for c in clauses)
    return _clause(constraint, value)


def _clause(constraint, value):
    pc, pv = _nums(constraint), _nums(value)
    if not pc or not pv:
        return True                       # nothing numeric to compare
    c = constraint.strip()
    if (c.startswith(">=") or c.endswith("+") or c.startswith(">")
            or c.startswith("~>")):
        n = min(len(pc), len(pv))
        return tuple(pv[:n]) >= tuple(pc[:n])
    if c.startswith("<="):
        n = min(len(pc), len(pv))
        return tuple(pv[:n]) <= tuple(pc[:n])
    if c.startswith("<"):
        n = min(len(pc), len(pv))
        return tuple(pv[:n]) < tuple(pc[:n])
    if c.startswith("^"):
        return pv[0] == pc[0]
    if c.startswith("~"):
        n = min(2, len(pc), len(pv))
        return pv[:n] == pc[:n]
    n = min(len(pc), len(pv))
    return pv[:n] == pc[:n]


def values_agree(fact, a, b):
    if fact == "runtime":
        return versions_agree(a, b)
    if fact == "services":
        # postgres vs postgres:15 -- an unpinned image agrees with a pinned one
        ta, tb = str(a).partition(":")[2], str(b).partition(":")[2]
        if not ta or not tb:
            return True
        return versions_agree(ta, tb)
    return _norm_cmd(a) == _norm_cmd(b)


def _norm_cmd(c):
    return " ".join(str(c).split()).rstrip(";").strip()


# ---------------------------------------------------------------- resolution
def _rank(provider, fact):
    order = PRECEDENCE.get(fact, ())
    return order.index(provider) if provider in order else len(order) + 1


def resolve(fact, key, claims, wf_rank=None):
    """Walk the table in order. First source that says something wins."""
    res = Resolution(fact, key)
    wf_rank = wf_rank or {}

    def sort_key(c):
        # Fixed precedence first; among CI claims prefer the workflow with the
        # most authority over "what runs on merge"; then file order, so the
        # result never depends on dict iteration order.
        return (_rank(c.provider, fact), -wf_rank.get(c.path, 0), c.path, c.line)

    ordered = sorted(claims, key=sort_key)
    res.unresolved = [c for c in ordered if not c.resolved]
    usable = [c for c in ordered if c.resolved]
    if not usable:
        return res

    res.winner = usable[0]
    # Once a source wins, take everything that source says -- but only from
    # the file that won. A matrix of Python versions in one workflow is the
    # set of versions tested, not five sources contradicting each other, and
    # commands in a release workflow are not how you run the repo.
    res.members = [c for c in usable
                   if c.provider == res.winner.provider
                   and c.path == res.winner.path]
    seen, uniq = set(), []
    for c in res.members:
        k = _norm_cmd(c.value)
        if k not in seen:
            seen.add(k)
            uniq.append(c)
    if fact == "services":
        # `postgres` and `postgres:17` are the same service; keep the pinned
        # one, since an untagged image tells the reader nothing.
        tagged = {str(c.value).partition(":")[0] for c in uniq if ":" in str(c.value)}
        uniq = [c for c in uniq if ":" in str(c.value)
                or str(c.value).partition(":")[0] not in tagged]
    res.members = uniq
    res.values = [c.value for c in res.members]

    members = set(id(c) for c in res.members)
    for c in usable:
        if id(c) in members:
            continue
        agrees = any(values_agree(fact, v, c.value) for v in res.values)
        if agrees:
            res.corroborations.append(c)
        elif fact in SINGLE_VALUED and c.provider != res.winner.provider:
            # Same-source variation is a matrix or a second job. A conflict
            # means two different kinds of source disagree.
            res.conflicts.append(c)
        else:
            res.skipped.append(c)
    return res


def reconcile(claims, wf_rank=None, prose_text=""):
    """Group claims by fact, resolve each, and collect the disagreements."""
    report = Report()
    groups = {}
    for c in claims:
        groups.setdefault((c.fact, c.key), []).append(c)

    for (fact, key), group in sorted(groups.items()):
        res = resolve(fact, key, group, wf_rank)
        report.resolutions.append(res)
        seen = {}
        for losing in res.conflicts:
            k = (key, losing.provider, _norm_cmd(losing.value))
            if k in seen:
                seen[k][2] += 1
                continue
            seen[k] = [res, losing, 1]
        for entry in seen.values():
            report.conflicts.append(tuple(entry))

    low = prose_text.lower()
    for res in report.resolutions:
        if not res.winner:
            continue
        # Verified but undocumented: the single most useful thing this tool
        # emits. "You also need a Postgres" is almost never in the README.
        if res.fact in ("services", "env") and res.tier == "verified":
            if not _mentioned(res.key, low):
                report.undocumented.append(res)
        # Prose-only: a command the README gives that nothing ever executes.
        if res.fact in ("install", "build", "test") and res.tier == "claimed":
            report.unverified.append(res)
    # Services first: "you also need a Postgres" is worth more than any single
    # environment variable.
    report.undocumented.sort(key=lambda r: (r.fact != "services", r.key))
    return report


def _mentioned(token, low):
    return bool(re.search(r"\b%s" % re.escape(str(token).lower()[:12]), low))


def table_as_text():
    """The precedence table, printable. The method is the deliverable."""
    out = []
    for fact, order in PRECEDENCE.items():
        arrows = "  ->  ".join(order)
        out.append("%-9s %s" % (fact, arrows))
    return "\n".join(out)
