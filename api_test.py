import time, json
import pandas as pd
import requests

# ── CONFIG ───────────────────────────────────────────────────────────────────
URL         = "https://httpbin.org/post"   # your endpoint
TOKEN       = "your-bearer-token"
INPUT_FILE  = "payloads.xlsx"
OUTPUT_FILE = "results.xlsx"
# ─────────────────────────────────────────────────────────────────────────────

df = pd.read_excel(INPUT_FILE).fillna("")

results = []
for _, row in df.iterrows():
    payload = row.to_dict()
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

    try:
        t0   = time.perf_counter()
        resp = requests.post(URL, json=payload, headers=headers, timeout=30)
        ms   = round((time.perf_counter() - t0) * 1000, 2)
        body = resp.text
    except Exception as e:
        ms, resp, body = 0, None, str(e)

    results.append({
        "Endpoint":        URL,
        "Payload":         json.dumps(payload),
        "Status Code":     resp.status_code if resp else "ERROR",
        "Response":        body,
        "Time Taken (ms)": ms,
    })

pd.DataFrame(results).to_excel(OUTPUT_FILE, index=False)
print(f"Done! Results saved to {OUTPUT_FILE}")
