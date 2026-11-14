#!/usr/bin/env python3
"""Launch the apeir ghost coin on pump.fun via PumpPortal.

Usage:
  launch.py create  WALLET_JSON MINT_KEY_JSON METADATA_URI OUT_JSON [--send]

METADATA_URI is a public URL of the token metadata JSON (see ../metadata.json).

Keys are loaded from the given paths (solana-keygen style JSON arrays); the
mint key is generated and written there (mode 600) if the file does not exist.
Nothing secret is ever printed.
"""
import base64, json, os, sys, time
import urllib.request
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

RPC = os.environ.get("SOLANA_RPC", "https://api.mainnet-beta.solana.com")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) apeir-launch"}

NAME = "apeir ghost"
SYMBOL = "APGHOST"


def http(url, data=None, headers=None, timeout=60):
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    return json.loads(http(RPC, body, {"Content-Type": "application/json"}))


def load_kp(path):
    return Keypair.from_bytes(bytes(json.load(open(path))))


def create(wallet_path, mint_path, uri, out_path, send):
    wallet = load_kp(wallet_path)
    if os.path.exists(mint_path):
        mint = load_kp(mint_path)
    else:
        mint = Keypair()
        fd = os.open(mint_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as f:
            json.dump(list(bytes(mint)), f)
    req = {"publicKey": str(wallet.pubkey()), "action": "create",
           "tokenMetadata": {"name": NAME, "symbol": SYMBOL, "uri": uri},
           "mint": str(mint.pubkey()), "denominatedInSol": "true", "amount": 0.001,
           "slippage": 10, "priorityFee": 0.0002, "pool": "pump"}
    raw = http("https://pumpportal.fun/api/trade-local", json.dumps(req).encode(),
               {"Content-Type": "application/json"})
    unsigned = VersionedTransaction.from_bytes(raw)
    tx = VersionedTransaction(unsigned.message, [mint, wallet])
    print("mint:", mint.pubkey())
    if not send:
        print("dry run: built and signed, not sent")
        return
    b64 = base64.b64encode(bytes(tx)).decode()
    r = rpc("sendTransaction", [b64, {"encoding": "base64", "skipPreflight": False,
                                      "preflightCommitment": "confirmed"}])
    if "error" in r:
        print("send error:", json.dumps(r["error"])[:600]); sys.exit(1)
    sig = r["result"]
    print("signature:", sig)
    json.dump({"mint": str(mint.pubkey()), "create_signature": sig},
              open(out_path, "w"))
    deadline = time.time() + 90
    while time.time() < deadline:
        st = rpc("getSignatureStatuses", [[sig], {"searchTransactionHistory": True}])["result"]["value"][0]
        if st:
            if st.get("err"):
                print("failed on chain:", st["err"]); sys.exit(2)
            if st.get("confirmationStatus") in ("confirmed", "finalized"):
                print("confirmed:", st["confirmationStatus"], "slot", st["slot"]); return
        time.sleep(1.5)
    print("timeout waiting for confirmation; do NOT resend, check signature", sig); sys.exit(3)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["create"] and len(a) >= 5:
        create(a[1], a[2], a[3], a[4], "--send" in a)
    else:
        print(__doc__); sys.exit(64)
