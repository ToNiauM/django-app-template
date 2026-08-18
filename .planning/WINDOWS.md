---
schema_version: 1
open_count: 1
waived_count: 0
fixed_count: 0
total_count: 1
last_updated: 2026-08-18T19:32:44.153Z
---

# Broken Windows Ledger

> Cross-phase defect register. `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 05 | deviation | .template-tests/test_05_nascimento.sh |  | A matriz test_04_*.py leva 79.9s; o preflight usa o contrato focado e a matriz completa roda separadamente. | open |  | 2026-08-18T19:32:44.153Z |  |

````json
[
  {
    "id": 1,
    "kind": "deviation",
    "phase": "05",
    "file": ".template-tests/test_05_nascimento.sh",
    "line": null,
    "description": "A matriz test_04_*.py leva 79.9s; o preflight usa o contrato focado e a matriz completa roda separadamente.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-08-18T19:32:44.153Z",
    "resolved_at": null
  }
]
````
