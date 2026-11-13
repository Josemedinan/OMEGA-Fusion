# Release candidate selection and provenance

> Paths relative to the repository root. Everything in the "V7" column was produced by one LibreLane run (`OMEGA_V15_RT`) and verified on those same files; V6 evidence is **not** reused for V7.

## Candidates considered
| Candidate | Evidence available | Eligible? |
|---|---|---|
| **V6** (`OMEGA_V6_ECO2` + `OMEGA_V6_SIGNOFF5`) | Full signoff on its own GDS (DRC, LVS, antenna, XOR, 9-corner STA) | Yes — kept as the verified baseline |
| **V14** (`OMEGA_V14_RT`) | STA summary, antenna and route-DRC logs only. The flow was stopped before stream-out; **no GDS, DRC, LVS or XOR exist**. Its run directory was later deleted (only the summary files remain in `physical_design/reports/iterations/OMEGA_V14_RT/`). | **No** — incomplete signoff; also equal to V7 on timing/slew/cap and with 1 fanout net |
| **V7 = V15** (`OMEGA_V15_RT`) | Complete flow: stream-out (Magic + KLayout), Magic/KLayout DRC, LVS, XOR, antenna, 9-corner STA (flow + independent), gate-level simulation | Yes |

## Objective comparison (flow limits unchanged)
| Metric | V6 | V7 | Better |
|---|---|---|---|
| Hold worst slack | +0.017 ns | +0.102 ns | V7 |
| Setup worst slack | +52.03 ns | +54.67 ns | V7 |
| Slew violations (max_ss) | 158 | 0 | V7 |
| Cap violations | 23 | 0 | V7 |
| Fanout violations | 83 nets | 1 net | V7 |
| DRC Magic / KLayout / route, LVS, XOR, antenna | 0 / 0 / 0, match, 0, 0 | 0 / 0 / 0, match, 0, 0 | tie |
| Area (std cells) / utilization | 0.849 mm² / 27.8 % | 0.852 mm² / 27.9 % | V6 (+0.3 %) |
| Caravel wrapper evidence | PDN, route DRC (V6 macro) | **none yet** | V6 |
**Selected: V7** as the physical-macro release candidate; **V6 stays published as the baseline** and as the only macro with wrapper-level evidence.

## File lineage of V7 (taken from the LibreLane state files of the final steps)
Producer → artifact (SHA-256 prefix; full hashes in `deliverables/v7/SHA256SUMS.original.txt`):
| Artifact | Produced by | SHA-256 | Consumed by |
|---|---|---|---|
| `odb` (`15-odb-cellfrequencytables`, post-fill) | fill insertion | `5b7da257…` | RCX, STA, Magic and KLayout stream-out |
| `def` (same step) | | `e7d6170d…` | Magic stream-out |
| Netlist `nl.v` (`14-openroad-fillinsertion`) | | `bab633b6…` (= `deliverables/v7/netlist/*.nl.v.gz`) | LVS (Netgen), gate-level simulation |
| Powered netlist `pnl.v` | | `2e8595a3…` (= `…pnl.v.gz`) | LVS |
| SDC | | `0ea694fc…` (= `deliverables/v7/timing/*.sdc`) | STA |
| SPEF max / min / nom (`16-openroad-rcx`) | RCX on the odb above | `d7666de0…` / `38280a7f…` / `e7e654d2…` | STA (flow and independent) |
| GDS (Magic, `19-magic-streamout`) | odb/def above | `275337f0…` (= release asset `omega_fusion_soc_asic_V7.gds.gz` after gunzip, round trip verified) | Magic DRC, KLayout DRC, XOR, SPICE extraction → LVS |
| KLayout GDS (`20-klayout-streamout`) | same odb | `87ea79e7…` | XOR (0 differences) |
| LEF | `write_abstract_lef -bloat_factor 3` on the pre-fill routed odb (`06-openroad-detailedrouting`) | `2c807a44…` (uncompressed) | Caravel wrapper (not yet run for V7) |
| Layout images `visuals/v7/*` | KLayout on the final DEF/GDS above | see `visuals/v7/` | README/gallery |
The LEF is derived from the routed database before fill; fill cells carry no signal connectivity, so the abstract (pins, outline, obstructions) is unaffected.
**Not** inherited from V6: DRC, LVS, XOR, antenna, STA, gate-level simulation — each was run on the V7 files listed above. **Inherited from V6 and therefore not valid for V7:** the Caravel wrapper PDN/route/antenna evidence.
