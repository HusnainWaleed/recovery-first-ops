# Recovery First Ops

A recovery drill for a fictional workplace asset inventory. Husnain Waleed's personal lab applies a systems administration lesson: a successful backup job is only useful if recovery is demonstrated.

**Implemented:** consistent SQLite backup, integrity and application-table checks, restore to a new file, overwrite protection and failure tests. This is a local database recovery tool; Kubernetes monitoring and disaster recovery orchestration are future work.

## Run a complete drill
Requires Python 3.12+. All records are synthetic. Use a new empty working directory or choose fresh database filenames.
```sh
python -m unittest discover -s tests -v
python recovery.py seed inventory.db
python recovery.py backup inventory.db backup.db
python recovery.py restore backup.db recovered.db
python recovery.py verify recovered.db
```
The final output should report `assets=2`. The tests also compare restored records, reject corrupt inputs, and confirm that an existing destination cannot be replaced.

## Incident runbook
1. Stop writes in a real incident; this lab does not manage application processes.
2. Verify the selected backup and identify its age and expected records.
3. Restore into a new location, preserving the original for investigation.
4. Validate integrity and expected business records. A row count alone is insufficient.
5. Point an isolated application at the restored database and test its critical workflow before any cutover.

## Record evidence
Record backup age, expected records, actual restored records, drill start/end and application verification results in [the drill template](docs/drill.md). Recovery time measured here covers a local drill only. No recovery objective or production improvement is claimed.

## Limits
No encrypted storage, offsite retention, scheduling, tamper resistance or access management is provided. SQLite integrity does not prove business completeness. Recovery into an existing file is intentionally disallowed. A real retention and recovery design needs separate review.

See [design decisions](docs/decisions.md) and [provenance](CONTRIBUTING.md).
