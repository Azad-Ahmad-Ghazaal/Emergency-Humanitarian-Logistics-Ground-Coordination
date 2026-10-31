# Genuine GitHub Copilot evidence — capture guide

The challenge asks for evidence that GitHub Copilot accelerated development. This guide prepares a short, reproducible task. It does not claim Copilot was used; capture evidence only after performing the interaction in GitHub Copilot.

## Suggested 3-minute Copilot session

Open this repository in an environment where GitHub Copilot Chat is available. Use the following prompt against the actual code:

> Review `relieflens/database.py` and `tests/test_database.py`. Identify edge cases in incident persistence that could cause malformed model output to be stored as trusted priority or signals. Suggest a minimal pytest regression test for one real issue. Do not change files until I approve. Explain why the test fails before the fix and passes after it.

Then ask:

> Review `relieflens/triage.py` and `tests/test_triage.py`. Find a concrete weakness in the bilingual keyword fallback. Suggest a minimal test using an actual Urdu emergency phrase already represented by the rules. Do not invent language coverage.

## What to capture

1. Screenshot of the actual Copilot Chat prompt and its response, with repository/file context visible.
2. Screenshot or diff of the resulting code/test change.
3. Successful GitHub Actions run URL showing the test passed.
4. One sentence explaining what Copilot contributed and what the developer reviewed or changed.

Sanitize personal information and never show API keys, tokens, private repository secrets, or wallet material.

## Submission note

Do not use a normal ChatGPT conversation, a fabricated transcript, or a hand-written screenshot as Copilot evidence. If Copilot is unavailable, report that evidence as pending rather than claiming the requirement is met.
