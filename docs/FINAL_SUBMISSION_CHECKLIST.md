# ReliefLens — Final Submission Evidence Checklist

This checklist separates repository work that is verifiably complete from challenge evidence that still requires an account, a human action, or a real capture. Do not mark a pending item complete without its evidence.

## Verified in GitHub

- [x] Public repository with MIT license.
- [x] CI workflow: [latest successful full test run](https://github.com/Azad-Ahmad-Ghazaal/Emergency-Humanitarian-Logistics-Ground-Coordination/actions/runs/41182912375).
- [x] Hosted Gemma 4 text API smoke test: [successful Gemini smoke run](https://github.com/Azad-Ahmad-Ghazaal/Emergency-Humanitarian-Logistics-Ground-Coordination/actions/runs/41182481982). This confirms hosted text model access using the repository secret; it does not verify local Ollama or hosted image inference.
- [x] Detailed README distinguishes local Ollama Gemma 4 from hosted Gemini API Gemma 4.
- [x] Demo walkthrough: [DEMO_SCRIPT.md](DEMO_SCRIPT.md).
- [x] SQLite incident register, CSV/JSON export, bilingual keyword fallback tests, and conservative image/chart prompts.

## Required evidence still pending

- [ ] **Local Gemma 4 deployment:** run `ollama pull gemma4:e2b` and test a sample report on the target laptop. The hosted Gemini API smoke test is not proof of local deployment.
- [ ] **Gemini multimodal image test:** run one real image through the hosted image path and retain a sanitized log or screenshot. The existing smoke test is text-only.
- [x] **Snowflake CoCo:** treated as an optional extension under the updated team plan; no live query is claimed or required for this submission path. Revisit only if the latest official challenge rubric still marks it mandatory.
- [ ] **Solana Agent Registry:** register the agent using the owner's wallet, then add the public profile URL and transaction signature. Draft metadata is not registration. Never share or commit a seed phrase/private key.
- [ ] **GitHub Copilot:** capture genuine screenshots or sanitized logs showing Copilot's actual prompt, response, and the code/debugging result. Do not fabricate this evidence.
- [ ] **End-to-end UI demo:** run `streamlit run app.py`, submit one sample report, show the incident board, and export CSV/JSON. GitHub CI does not launch and visually verify the Streamlit UI.

## Suggested judge demo order

1. Explain the offline-first field-report problem and safety boundary.
2. Show the Streamlit report form and incident board with a sample report.
3. Explain local Gemma vs hosted Gemini as two separate execution paths.
4. Show the successful CI and hosted text smoke-test links.
5. Show the Solana registration guide; provide the transaction link only after registration.
6. Show genuine Copilot evidence only after it has been captured.

## Safety and honesty

ReliefLens is a prototype decision-support tool, not a dispatch system, medical diagnosis tool, or structural-safety certification. Model outputs, transcriptions, extracted counts, and keyword priorities require human verification. Never invent an on-chain signature, Snowflake result, Copilot screenshot, or local model test.
