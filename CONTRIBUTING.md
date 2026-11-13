# Contributing

* Keep claims tied to evidence: a result goes into the docs only with its log/report path. Use PASS / FAIL / UNVERIFIED; absence of a report is never PASS.
* Do not relax constraints or Liberty limits, and do not disable checkers, to turn a FAIL into a PASS. ECOs go on a new variant (run tag) and are re-verified; V6 stays the verified baseline.
* RTL changes must keep `bash scripts/run_all.sh` green and update the architecture docs.
* No generated databases (ODB/DEF/SPEF/GDS) in git; large artifacts go to release assets with a SHA-256.
* Commit messages: imperative, one logical change.
