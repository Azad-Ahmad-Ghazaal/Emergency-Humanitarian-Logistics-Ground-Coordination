# ReliefLens Solana Agent Registry — registration checklist

## Current state

**Not registered on-chain.** This folder contains a draft metadata card only. A valid on-chain registration requires a wallet-controlled transaction and a public transaction signature.

## Registry route

Use the official Solana Agent Registry: https://solana.com/agent-registry

The registry describes on-chain agent identity and currently lists an approximate registration fee of 0.009 SOL. Confirm the live fee and network in the official UI before signing.

## What the project owner must do

1. Open the official registry and connect a wallet you control.
2. Review the registration flow, metadata URL, network, and fee.
3. Publish or host the reviewed metadata card at a stable public URL (the GitHub raw file URL can be used if accepted by the registry).
4. Sign the registration transaction in your wallet.
5. Copy the confirmed transaction signature and public agent identity/profile URL.
6. Add those public values to this file and the README after confirming the transaction on the relevant explorer.

## Security

- Never share or commit a seed phrase, private key, wallet JSON, or signing secret.
- Do not let an untrusted website request broad wallet permissions.
- Do not delegate agent-wallet execution authority for this prototype.
- The repository assistant cannot sign or submit a wallet transaction on the owner's behalf.

## Uptime diagnostics

A registration record proves identity, not continuous uptime. If uptime evidence is required, implement a separate monitor that emits timestamped health checks and publish the monitoring method and endpoint. Do not describe a static registration as proof of uptime.
