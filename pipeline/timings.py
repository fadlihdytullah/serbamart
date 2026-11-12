import json
from pathlib import Path

results = json.loads(Path("transform/target/run_results.json").read_text())
nodes = sorted(results["results"], key=lambda r: r["execution_time"], reverse=True)

print(f"{'type':<9} {'name':<46} {'seconds':>7}")
for node in nodes[:8]:
    kind, _, name = node["unique_id"].split(".")[:3]
    print(f"{kind:<9} {name[:46]:<46} {node['execution_time']:>7.2f}")

work = sum(node["execution_time"] for node in nodes)
print(f"\n{len(nodes)} nodes, {work:.1f} s of work in {results['elapsed_time']:.1f} s")
