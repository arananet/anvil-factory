# Scenario checks: operator-requirements

Written before implementation. Placed here, not under tests/, because the work
order and spec R7 forbid creating or modifying any file under tests/. These are
runnable checks (bash, run from the repo root) that the reviewer and checks
station can execute against the builder's output. Each maps to a spec scenario.

Let DOC=docs/OPERATOR-REQUIREMENTS.md.

## S1 (R1, R2): permission to operation to failure

The document exists, has the three sections, and names each permission with its
proving operation and failure.

    test -f docs/OPERATOR-REQUIREMENTS.md
    for h in GitHub Cloudflare "Placement and care"; do grep -qiE "^#+ .*$h" $DOC || echo "MISSING heading: $h"; done
    for p in "Contents" "Actions" "Issues" "Administration" "Secrets"; do grep -q "$p" $DOC || echo "MISSING permission: $p"; done
    for t in custom.github "403" "PATCH" "PUT" "topics" "write-only" "merges API" "webhooks" "labels" "Pages" "social preview" "Settings UI" "empty trigger commits" "report comment"; do grep -q "$t" $DOC || echo "MISSING term: $t"; done

Expected: no MISSING lines. Reviewer judgment: each permission entry states both
the working call and the observed failure without it.

## S2 (R3): credential kind distinction

    for t in "client secret" "personal access token" "401" "Developer settings" "Fine-grained tokens" "Repository access" "Repository permissions"; do grep -qi "$t" $DOC || echo "MISSING term: $t"; done

Expected: no MISSING lines. The document names no app and no value.

## S3 (R4): gateway shape

    for t in custom.cloudflare "API Tokens Edit" "415" "9109" arananet-ai-gateway x-api-key cf-aig-authorization ANTHROPIC_API_KEY ANTHROPIC_CUSTOM_HEADERS "2009" CF_AIG_TOKEN "Unified Billing" "BYOK" "log collection" Wrangler; do grep -qi -- "$t" $DOC || echo "MISSING term: $t"; done

Expected: no MISSING lines.

## R5: closing section

    # last H2 heading must be the placement and care section
    grep -E '^## ' $DOC | tail -1 | grep -qi "placement" || echo "FAIL: placement and care is not the closing section"
    grep -qi "exact shape" $DOC || echo "MISSING lesson one (probe in consumer shape)"
    grep -qiE "existing (reservation|ticket|secret)|reservation" $DOC || echo "MISSING lesson two"

## S4 (R6): no credential values

Scan every file the run produces (DOC, README.md, CHANGELOG.md, and this
directory) for credential-shaped strings. Must print nothing.

    F="$DOC README.md CHANGELOG.md"
    grep -nE 'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|Bearer +[A-Za-z0-9._-]{20,}|[A-Za-z0-9_-]{40,}' $F | grep -vE 'https?://|\.md|\]\(' 

Also confirm no token id: no 32-char hex strings in DOC.

    grep -nE '\b[0-9a-f]{32}\b' $DOC

## R7: scope and style

    git diff --name-only main... | sort    # allowed: CHANGELOG.md, README.md, docs/OPERATOR-REQUIREMENTS.md (plus this spec directory)
    git diff --name-only main... | grep '^tests/' && echo "FAIL: tests/ touched"
    grep -n 'OPERATOR-REQUIREMENTS' README.md           # row in the Documentation table, matching neighbors' style
    grep -n -A4 -i 'unreleased' CHANGELOG.md | grep -i 'operator'
    grep -nP '\x{2014}|\x{2013}' $DOC README.md CHANGELOG.md   # no em or en dashes; must print nothing
    python -m pytest -q                                  # full suite stays green
