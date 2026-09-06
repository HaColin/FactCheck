#!/usr/bin/env -S rote play run
/**
 * @rote-frontmatter
 * ---
 * name: factcheck
 * description: 'Find out how to actually run a GitHub repo: reconcile what its CI executes against what its README claims. Surfaces the Postgres or Redis services CI needs that the README never mentions, the real runtime versions, the true install and test commands, and every place the documentation contradicts the build. Emits FACTCHECK.md and an executable factcheck.sh, with a file and line behind every claim.'
 * source: https://github.com/HaColin/FactCheck
 * provenance:
 *   author: colinha888@gmail.com
 * parameters:
 * - name: out_dir
 *   type: string
 *   required: false
 *   default: .
 *   description: Where to write FACTCHECK.md and factcheck.sh. Defaults to the directory you run from; a relative path resolves there too. Created if missing.
 * - name: mine_issues
 *   type: string
 *   required: false
 *   default: no
 *   description: '''yes'' also searches the issue tracker for reported setup problems. This is the only step that spends GitHub API rate limit, and its result varies over time; everything else is derived from the commit alone.'
 * - name: repo_url
 *   type: string
 *   required: true
 *   description: Public GitHub repository URL, e.g. https://github.com/netbox-community/netbox
 * metadata:
 *   version: 1.4.0
 *   rote_version: 0.80.0
 *   contract:
 *     atomic: true
 *     input:
 *       type: none
 *     output:
 *       format: json
 *       destination: stdout
 *     composable: true
 *   status: released
 *   kind: atomic
 *   flow_type: sequential
 *   execution_model: steps_with_presentation
 *   requires_sessions: false
 *   discoverability:
 *     tags:
 *     - github
 *     - ci
 *     - readme
 *     - documentation
 *     - onboarding
 *     - setup
 *     - install
 *     - developer-experience
 *     - github-actions
 *     - workflows
 *     - repository
 *     - provenance
 *     - stale-docs
 *     - getting-started
 *     - build
 *     - devex
 * presentation_fixtures:
 *   reconcile: resources/presentation-fixtures/reconcile/fixture.yaml
 * steps:
 *   reconcile:
 *     type: process.exec
 *     argv:
 *     - python3
 *     - '@resource{factcheck.py}'
 *     - $repo_url
 *     - --quiet-ci
 *     - -o
 *     - $out_dir/FACTCHECK.md
 *     - -s
 *     - $out_dir/factcheck.sh
 *     - --issues
 *     - $mine_issues
 *     - --json-summary
 *     timeout_ms: 300000
 * ---
 */

const presentationSdk = await import("__ROTE_PRESENTATION_SDK__").catch((cause) => {
  throw new Error(
    "This is a rote steps presentation program. Run it with `rote play run <name>`.",
    { cause },
  );
});
const { FlowOutput, loadPresentationContext, stepName, isProcessExecBody } =
  presentationSdk;

const out = new FlowOutput();
const ctx = await loadPresentationContext();
const step = ctx.step(stepName("reconcile"));

type Summary = {
  repo?: string;
  url?: string;
  commit?: string;
  branch?: string;
  primary_workflow?: string | null;
  primary_triggers?: string[];
  has_ci?: boolean;
  runtime?: Record<string, string>;
  services?: Record<string, string>;
  counts?: Record<string, number>;
  gotchas?: { enabled?: boolean; status?: string; count?: number };
  artifacts?: Record<string, string | null>;
};

// The analysis prints one JSON object as its last stdout line. Parsing that
// beats regexing the human output above it, and keeps this body honest about
// what it does not know.
function readSummary(text: string): Summary | null {
  const lines = text.trimEnd().split("\n");
  for (let i = lines.length - 1; i >= 0 && i > lines.length - 6; i--) {
    const line = lines[i].trim();
    if (!line.startsWith("{")) continue;
    try {
      return JSON.parse(line) as Summary;
    } catch {
      // Not the summary line; keep looking rather than guessing.
    }
  }
  return null;
}

function pairs(obj: Record<string, string> | undefined): string {
  const entries = Object.entries(obj ?? {});
  return entries.length ? entries.map(([k, v]) => `${k} ${v}`).join(", ") : "none";
}

const outcome = step.outcome;
if (outcome.status === "failed") {
  out.human(`FACTCHECK failed: ${outcome.output.message}`);
  out.summary("FACTCHECK failed.");
  out.result({ ok: false, status: "failed", message: outcome.output.message });
} else if (outcome.status === "skipped" || outcome.status === "blocked") {
  const reason = outcome.output.reason;
  out.human(`FACTCHECK did not run: ${reason}`);
  out.summary("FACTCHECK did not run.");
  out.result({ ok: false, status: outcome.status, reason });
} else {
  const body = outcome.output.body;
  const proc = isProcessExecBody(body) ? body : null;
  const stdout = proc?.stdout?.text ?? "";
  const summary = readSummary(stdout);
  // Paths come from the analysis itself, absolute, so the caller can open them.
  const files = Object.entries(summary?.artifacts ?? {})
    .filter(([, path]) => typeof path === "string" && path.length > 0)
    .map(([label, path]) => ({ label, path: path as string }));

  const lines: string[] = [];
  if (summary) {
    lines.push(`${summary.repo ?? "repository"} @ ${(summary.commit ?? "").slice(0, 12)}`);
    lines.push(
      summary.has_ci
        ? `Primary CI: ${summary.primary_workflow} (on ${(summary.primary_triggers ?? []).join(", ")})`
        : "No CI runs on merge in this repo, so nothing here is verified.",
    );
    lines.push(`Runtime:  ${pairs(summary.runtime)}`);
    lines.push(`Services: ${pairs(summary.services)}`);
    const c = summary.counts ?? {};
    lines.push(
      `Findings: ${c.conflicts ?? 0} conflict(s), ${c.undocumented ?? 0} required but undocumented, ` +
        `${c.commands ?? 0} command(s), ${c.env_vars ?? 0} env var(s)`,
    );
    const g = summary.gotchas;
    if (g?.enabled) {
      lines.push(
        g.status === "ok"
          ? `Tracker: ${g.count ?? 0} reported setup problem(s)`
          : `Tracker: skipped (${g.status}) — the rest of the document is unaffected`,
      );
    }
  } else {
    // No summary line means the analysis printed something unexpected. Say so
    // rather than reporting zeros as if they were findings.
    lines.push("The analysis produced no machine-readable summary; see the artifacts.");
  }
  lines.push("");
  if (files.length) {
    lines.push("Written:");
    for (const f of files) lines.push(`  ${f.label}: ${f.path}`);
  } else {
    lines.push("No artifacts were written.");
  }

  out.human(lines.join("\n"));
  out.summary(
    summary
      ? `${summary.repo}: ${summary.counts?.conflicts ?? 0} conflict(s), ` +
        `${summary.counts?.undocumented ?? 0} undocumented requirement(s)`
      : "FACTCHECK completed; summary unavailable.",
  );
  out.result({
    ok: true,
    run_id: ctx.run.run_id,
    summary: summary ?? null,
    artifacts: files,
  });
}
