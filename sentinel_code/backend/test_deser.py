from app.core.test_harness import test_harness
from app.core.vulnerability_config import get_payloads_for_type

print("starting deserialization test")

payloads = get_payloads_for_type("DESERIALIZATION")
print("payloads", payloads)

results = []
for p in payloads:
    print("--- trying", p)
    res = test_harness.run_attack(p, vuln_type="DESERIALIZATION")
    print("result ->", res)
    results.append((p, res))

# write results into a file for later inspection
with open("deser_results.txt", "w", encoding="utf-8") as f:
    for p, r in results:
        f.write(f"payload: {p}\n")
        f.write(f"result: {r}\n")
        f.write("---\n")

print("done")
