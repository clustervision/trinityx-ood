# TRIX-1927 — QA Report Summary & Engineering Decision

**Date:** 28 July 2026  
**Ticket:** TRIX-1927 (Rack chassis image optimisation)  
**QA reference:** *Rack-Chassis-Image-Optimisation-QA-Report.pdf* (slurming.cluster, Playwright headless Edge)

---

## Executive summary

QA confirmed that the chassis PNG re-export **worked as intended**: all 25 vendor files are 240 px wide, the full chassis set is ~470 KB, and a realistic load (32 devices across five racks) paints in **~918 ms** from an empty browser cache with only **20 image requests**. The originally reported **~30 s first load was not reproduced** under direct HTTP access; the most plausible remaining cause is the **VNC remote-display path**, which QA did not measure.

However, the optimisation pass also surfaced **four defects**. Three are accepted for fix in this ticket; one is deferred; chassis PNG compression is considered **complete** and will not receive further effort.

---

## QA results at a glance

| Area | Result | Notes |
|------|--------|-------|
| PNG downscaling (TC-03) | **PASS** | 240 px wide, 4.8–44.9 KB per file, 469.9 KB total |
| Cold-load performance (TC-10) | **PASS** | 918 ms to paint 32 chassis; 327 KB on the wire |
| Image reuse (TC-12) | **PASS** | 20 requests for 32 devices (preload + dedup) |
| Interaction (TC-13) | **PASS** | Flip 242 ms, 2× zoom 252 ms |
| All assets served (TC-02, TC-06) | **FAIL** | HP case mismatch; ASUS/Gigabyte artwork missing |
| PNG integrity (TC-04) | **FAIL** | 3 corrupt `devices-*.png`; `switch-off.png` is JPEG |
| Asset weight balance (TC-05) | **FAIL** | `boxicons.svg` (1.1 MB) dominates; not in scope |
| Warm load (TC-11) | **PARTIAL** | Variance from controller, not assets |
| Drag-and-drop (TC-14) | **INCONCLUSIVE** | Automation limitation with multiple racks |

**Score:** 9 / 15 passed · 4 failed · 1 partial · 1 inconclusive

---

## Decision

### Accepted fixes (this change set)

| Defect | Severity | Decision | Implementation |
|--------|----------|----------|----------------|
| **D1** — HP/HPE renders blank (`hp-*.png` vs `HP-*.png`) | HIGH | **Fix** | Rename shipped files to lowercase `hp-{1,2,3,4,8}u.png` to match the resolver |
| **D2** — ASUS/Gigabyte resolve to `undefined` | HIGH | **Fix (fallback)** | No vendor-specific artwork will be added. Vendors without shipped chassis art (ASUS, Gigabyte, and any future unknown) **fall back to `default-*` images** |
| **D4** — `switch-off.png` is JPEG with `.png` extension | LOW | **Fix** | Re-export as a valid PNG |

### Deferred / out of scope

| Item | Decision | Rationale |
|------|----------|-----------|
| **D3** — Corrupt `devices-2u/3u/4u.png` | **Defer** | Latent: Vite currently inlines these as base64; not user-visible today. Fix in a follow-up with binary re-export + CI PNG-signature check |
| **D5** — `boxicons.svg` (1.1 MB) | **Defer** | Separate optimisation; 2.6× entire chassis set. Subsetting icons is valuable but not part of TRIX-1927 |
| Further chassis PNG compression | **Reject** | QA recommendation #6: 470 KB total, 918 ms cold paint — **not the constraint** |
| 30 s load complaint | **Investigate separately** | Not reproducible on slurming; re-measure on customer VNC (16-bit vs 24-bit) before more asset work |
| Resolver fallback to `default-*` for all unknown vendors | **Accept (extends D2)** | Prevents any future `assets/undefined` URL for unrecognised or unprovisioned vendors |

### Performance conclusion

The ticket premise — *many large chassis PNGs cause slow first paint* — is **not supported** by QA under realistic HTTP conditions. Image weight was reduced successfully, but the measured bottleneck for the reported user experience is **likely outside the asset payload** (VNC encoding / remote framebuffer). No additional chassis image work is planned for TRIX-1927.

---

## Changes made (rack-app)

1. **`src/assets/img/`** — Renamed `HP-*.png` → `hp-*.png` (D1)
2. **`src/utils/deviceImageUrls.ts`** — Restrict chassis lookup to vendors with shipped artwork (`supermicro`, `dell`, `hp`, `lenovo`); all others use `default-*` (D2)
3. **`src/assets/img/switch-off.png`** — Converted from JPEG to valid PNG (D4)

Rebuild and redeploy `rack/app/assets/` in **trinityx-ood** (including `index.js` and renamed `hp-*.png` files) to apply on cluster.

---

## Sign-off intent

- Chassis PNG optimisation: **complete, no further compression**
- QA defects D1, D2, D4: **fixed in rack-app**
- QA defect D3, D5, VNC re-measurement: **tracked separately**
- Ready for QA re-run of TC-02, TC-04 (partial), and TC-06 after OOD deploy
