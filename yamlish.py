"""Line-tracking YAML subset parser. Stdlib only.

Scoped to the YAML that CI config actually uses: block mappings, block
sequences, block scalars, one-line flow collections, quoting, comments.
Every value produced remembers the 1-based line it came from, because
FACTCHECK cites file:line for every claim it makes.

Deliberately NOT YAML 1.1: `on:` stays the string "on" rather than
becoming True, which is what a workflow file means by it.
"""


class S(str):
    """Scalar string that remembers its source line."""
    __slots__ = ("line",)

    def __new__(cls, value, line=0):
        o = super().__new__(cls, value)
        o.line = line
        return o


class M(dict):
    """Mapping that remembers its own line and the line of each key."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.line = 0
        self.klines = {}

    def kline(self, key, default=0):
        return self.klines.get(key, default)


class L(list):
    def __init__(self, *a):
        super().__init__(*a)
        self.line = 0


def _expand(raw):
    return raw.replace("\t", "    ")


def _indent_of(raw):
    return len(raw) - len(raw.lstrip(" "))


def strip_comment(s):
    """Drop a trailing # comment, respecting quotes."""
    q = None
    for i, c in enumerate(s):
        if q:
            if c == "\\" and q == '"':
                continue
            if c == q:
                q = None
        elif c in "\"'":
            q = c
        elif c == "#" and (i == 0 or s[i - 1] in " \t"):
            return s[:i].rstrip()
    return s.rstrip()


def find_key_sep(s):
    """Index of the ':' that separates a block mapping key, else -1."""
    q = None
    for i, c in enumerate(s):
        if q:
            if c == "\\" and q == '"':
                continue
            if c == q:
                q = None
        elif c in "\"'":
            q = c
        elif c in "[{":
            return -1  # flow collection, not a block key
        elif c == ":" and (i + 1 == len(s) or s[i + 1] in " \t"):
            return i
    return -1


def scan_flow(s, depth=0, q=None):
    """Consume a flow fragment, tracking bracket depth outside quotes.

    Flow collections in CI config routinely span lines (`paths: [` then one
    entry per line). Returns (text, depth, quote_state) so the caller can keep
    pulling lines until depth returns to zero.
    """
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if q:
            out.append(c)
            if c == "\\" and q == '"' and i + 1 < len(s):
                out.append(s[i + 1])
                i += 2
                continue
            if c == q:
                q = None
            i += 1
            continue
        if c in "\"'":
            q = c
        elif c == "#" and (i == 0 or s[i - 1] in " \t"):
            break
        elif c in "[{":
            depth += 1
        elif c in "]}":
            depth -= 1
        out.append(c)
        i += 1
    return "".join(out), depth, q


def unquote(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        body = s[1:-1]
        if s[0] == '"':
            body = (body.replace('\\"', '"').replace("\\n", "\n")
                        .replace("\\t", "\t").replace("\\\\", "\\"))
        else:
            body = body.replace("''", "'")
        return body
    return s


def _strip_anchor(s):
    """Drop a leading &anchor / !!tag token; keep any value after it."""
    while s[:1] in ("&", "!"):
        parts = s.split(None, 1)
        s = parts[1].strip() if len(parts) > 1 else ""
        if not s:
            break
    return s


class Parser:
    def __init__(self, text):
        self.lines = [_expand(x) for x in text.splitlines()]
        self.i = 0

    # -- line cursor -------------------------------------------------
    def peek(self):
        """Next significant line as (indent, stripped_content, lineno)."""
        while self.i < len(self.lines):
            raw = self.lines[self.i]
            s = raw.strip()
            if not s or s.startswith("#") or s in ("---", "..."):
                self.i += 1
                continue
            return (_indent_of(raw), s, self.i + 1)
        return None

    # -- nodes -------------------------------------------------------
    def parse_node(self, indent):
        p = self.peek()
        if p is None:
            return S("", 0)
        _, content, _ = p
        if content == "-" or content.startswith("- "):
            return self.parse_sequence(indent)
        return self.parse_mapping(indent)

    def parse_mapping(self, indent):
        m = M()
        while True:
            p = self.peek()
            if p is None or p[0] != indent:
                break
            ind, content, ln = p
            if content == "-" or content.startswith("- "):
                break
            sep = find_key_sep(strip_comment(content))
            if sep < 0:
                break
            key = unquote(content[:sep])
            rest = strip_comment(content[sep + 1:]).strip()
            self.i += 1
            if not m.line:
                m.line = ln
            m.klines[key] = ln
            m[key] = self.parse_value(rest, ind, ln)
        return m

    def parse_sequence(self, indent):
        seq = L()
        while True:
            p = self.peek()
            if p is None or p[0] != indent:
                break
            ind, content, ln = p
            content = strip_comment(content)  # `- # note` is an empty item
            if content != "-" and not content.startswith("- "):
                break
            if not seq.line:
                seq.line = ln
            rest = "" if content == "-" else content[2:].strip()
            if rest == "":
                self.i += 1
                nxt = self.peek()
                seq.append(self.parse_node(nxt[0]) if nxt and nxt[0] > ind
                           else S("", ln))
                continue
            raw = self.lines[ln - 1]
            dash = raw.index("-", ind)
            body = raw[dash + 1:]
            rest_indent = dash + 1 + (len(body) - len(body.lstrip(" ")))
            if find_key_sep(strip_comment(rest)) >= 0:
                # "- key: value": re-indent in place so the mapping parser
                # picks up this line and its siblings, line numbers intact.
                self.lines[ln - 1] = " " * rest_indent + rest
                seq.append(self.parse_mapping(rest_indent))
            else:
                self.i += 1
                seq.append(self.parse_value(rest, rest_indent, ln))
        return seq

    def read_flow(self, text, ln):
        """A flow collection, continuing across lines until brackets balance."""
        buf, depth, q = scan_flow(text)
        while depth > 0 and self.i < len(self.lines):
            seg, depth, q = scan_flow(self.lines[self.i].strip(), depth, q)
            buf += " " + seg
            self.i += 1
        return parse_flow(buf, ln)

    def _fold_plain(self, ind):
        """Continuation lines of a multi-line plain scalar.

        `if: cond &&` wrapped onto a deeper line is common in CI config, and
        treating the continuation as a new key silently truncates the rest of
        the document -- the whole job's steps disappear.
        """
        out = []
        while True:
            p = self.peek()
            if p is None or p[0] <= ind:
                break
            _, content, _ = p
            if content == "-" or content.startswith("- "):
                break
            if find_key_sep(strip_comment(content)) >= 0:
                break
            out.append(strip_comment(content).strip())
            self.i += 1
        return out

    def parse_value(self, rest, ind, ln):
        if rest[:1] in ("|", ">") and (len(rest) == 1 or rest[1] in "-+0123456789"):
            return self.read_block_scalar(rest, ind, ln)
        rest = _strip_anchor(rest)
        if rest == "":
            nxt = self.peek()
            if nxt and (nxt[1] == "-" or nxt[1].startswith("- ")) and nxt[0] >= ind:
                return self.parse_sequence(nxt[0])
            if nxt and nxt[0] > ind:
                if nxt[1][:1] in "[{":
                    self.i += 1          # flow collection opening on its own line
                    return self.read_flow(nxt[1], nxt[2])
                if find_key_sep(strip_comment(nxt[1])) < 0:
                    return S(" ".join(self._fold_plain(ind)), ln)  # plain scalar block
                return self.parse_node(nxt[0])
            return S("", ln)
        if rest[0] in "[{":
            return self.read_flow(rest, ln)
        cont = self._fold_plain(ind)
        if cont:
            return S(" ".join([unquote(rest)] + cont), ln)
        return S(unquote(rest), ln)

    def read_block_scalar(self, header, parent_indent, ln):
        fold = header[0] == ">"
        chomp = "-" if "-" in header else ("+" if "+" in header else "")
        digits = "".join(c for c in header if c.isdigit())
        out, base = [], None
        while self.i < len(self.lines):
            raw = self.lines[self.i]
            if raw.strip() == "":
                out.append("")
                self.i += 1
                continue
            ind = _indent_of(raw)
            if ind <= parent_indent:
                break
            if base is None:
                base = parent_indent + int(digits) if digits else ind
            out.append(raw[base:] if len(raw) > base else "")
            self.i += 1
        if chomp != "+":
            while out and out[-1] == "":
                out.pop()
        if fold:
            folded, buf = [], []
            for line in out:
                if line == "":
                    folded.append(" ".join(buf))
                    buf = []
                    folded.append("")
                else:
                    buf.append(line.strip())
            if buf:
                folded.append(" ".join(buf))
            out = folded
        text = "\n".join(out)
        if chomp == "" and text:
            text += "\n"
        return S(text, ln)


def parse_flow(s, ln):
    """One-line flow collection: [a, b] or {k: v, k2: v2}."""
    val, _ = _flow(s, 0, ln)
    return val


def _flow(s, i, ln):
    while i < len(s) and s[i] == " ":
        i += 1
    if i >= len(s):
        return S("", ln), i
    if s[i] == "[":
        seq = L()
        seq.line = ln
        i += 1
        while i < len(s):
            while i < len(s) and s[i] in " ,":
                i += 1
            if i < len(s) and s[i] == "]":
                return seq, i + 1
            v, i = _flow(s, i, ln)
            seq.append(v)
        return seq, i
    if s[i] == "{":
        m = M()
        m.line = ln
        i += 1
        while i < len(s):
            while i < len(s) and s[i] in " ,":
                i += 1
            if i < len(s) and s[i] == "}":
                return m, i + 1
            k, i = _flow_token(s, i, ln, ":,}]")
            while i < len(s) and s[i] in ": ":
                i += 1
            v, i = _flow(s, i, ln)
            m[unquote(k)] = v
            m.klines[unquote(k)] = ln
        return m, i
    return _flow_token(s, i, ln, ",}]")


def _flow_token(s, i, ln, stops):
    if s[i] in "\"'":
        q, j = s[i], i + 1
        while j < len(s):
            if s[j] == "\\" and q == '"':
                j += 2
                continue
            if s[j] == q:
                break
            j += 1
        return S(unquote(s[i:j + 1]), ln), j + 1
    j = i
    while j < len(s) and s[j] not in stops:
        j += 1
    return S(unquote(s[i:j].strip()), ln), j


def load(text):
    p = Parser(text)
    first = p.peek()
    if first is None:
        return M()
    return p.parse_node(first[0])


def load_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return load(fh.read())
