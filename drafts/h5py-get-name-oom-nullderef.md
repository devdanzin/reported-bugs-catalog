---
slug: h5py-get-name-oom-nullderef
title: h5py get_name unchecked malloc -> PyBytes_FromString(NULL) segv (+ @with_phil Py_INCREF(NULL))
tool: fusil-plugin-h5py
mode: oom
target_repo: h5py/h5py
findings: 2
status: fix-verified, not filed
filed: false
---

**Found-but-not-filed** — excluded from filed-artifact counts; contributes to the
*unfiled-findings* number.

- **Tool:** fusil-plugin-h5py (oom)
- **Target:** h5py/h5py
- **Findings (est.):** 2
- **Why unfiled:** User reviewing before filing; G-1 fix verified (fix.patch on h5i.templ.pyx), G-12 root-caused (Cython-gen, likely upstream).
- **Source (local, not in this repo):** `/home/danzin/crashers/h5py_get_name_oom_nullderef/REPORT.md`
