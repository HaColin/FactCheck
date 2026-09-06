"""A claim: one fact, one value, one place it came from.

Everything FACTCHECK asserts is a Claim, and a Claim without a file and line
is not allowed to exist. That is the whole provenance rule, enforced by the
constructor rather than by remembering to cite things later.
"""

# Which sources are executed on every merge, and which are prose someone
# wrote once. This is the verified/claimed split the output is built around.
VERIFIED = {
    "toolchain-file", "ci-setup", "ci-run", "ci-services", "ci-env",
    "ci-runs-on", "dockerfile-from", "dockerfile-run", "lockfile",
    "docker-compose",
}
CLAIMED = {
    "manifest-engines", "manifest-scripts", "env-example", "readme",
}


class Claim:
    __slots__ = ("fact", "key", "value", "provider", "path", "line",
                 "resolved", "note", "data")

    def __init__(self, fact, key, value, provider, path, line,
                 resolved=True, note="", data=None):
        if not path or not line:
            raise ValueError("claim without provenance: %r %r" % (fact, value))
        self.fact = fact            # runtime | install | build | test | ...
        self.key = key              # tool name, service name, env var name
        self.value = value
        self.provider = provider    # which source produced it
        self.path = path            # repo-relative file
        self.line = line
        # False when the source says something we cannot read literally, e.g.
        # a CI value of ${{ steps.versions.outputs.erlang }}. Such a claim is
        # recorded but never wins -- precedence falls through to the next
        # source instead of printing an expression as an answer.
        self.resolved = resolved
        self.note = note
        # Structured extras the renderers need without parsing prose: a
        # service's declared ports and env, for instance.
        self.data = data or {}

    @property
    def tier(self):
        return "verified" if self.provider in VERIFIED else "claimed"

    @property
    def cite(self):
        return "%s:%d" % (self.path, self.line)

    def __repr__(self):
        return "<%s %s=%s %s %s%s>" % (self.fact, self.key, self.value,
                                       self.provider, self.cite,
                                       "" if self.resolved else " UNRESOLVED")
