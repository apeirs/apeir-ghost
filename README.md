# apeir ghost (APGHOST)

A pump.fun coin made for the make.fun $1000 bounty. Image is make.fun's own mascot, unmodified.

- Mint: `CiXDMWXismTZTuPAtFXDVxBh4iqNwtMndh23qe1wBTJV`
- Create signature: `3MTdiRzNrVN1s6UXUHxj1bxQY15HV81fk6bqSknaYmgPGrawwnRAYKgasBgsQLUJfEcRzcvDF2rTzVPXJSS5oK8L`

## How it was launched

1. `metadata.json` was published as a public gist; its revision-pinned raw URL is the token URI.
2. `launch/launch.py` asked PumpPortal's trade-local API for a create transaction (0.001 SOL dev buy),
   signed it with the mint keypair and the creator wallet, and sent it once to Solana mainnet.
3. The transaction was confirmed and the mint checked on chain.

`main.ts` copies `LAUNCH.json` from `MAKEFUN_BOT_DIR` (default `/bot`) to `MAKEFUN_OUTPUT_DIR`
(default `/output`). Run with `node main.ts`.
