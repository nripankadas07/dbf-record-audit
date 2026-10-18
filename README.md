# dbf-record-audit

Audit dBASE III binary table structure and active/deleted cell quality without coercing numeric data.

For: Legacy GIS/data ingestion maintainers reviewing a small DBF before migration. Silent float conversion, deletion filtering and cleanup can obscure malformed dates or decimal representations.

## Quickstart

Python3.10+; no runtime packages/network. Building the wheel needs setuptools from the normal Python registry.

```sh
git clone https://github.com/nripankadas07/dbf-record-audit.git
cd dbf-record-audit
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/dbf-record-audit --make-example example.dbf
.venv/bin/dbf-record-audit example.dbf
```

Generator creates a new invented DBF and refuses overwrite. Exit0: two active records sum exactly to0.30; one deleted record separately sums to9.99. A valid leap-day date is retained.

Windows equivalents use `.venv\Scripts\python.exe` and `.venv\Scripts\dbf-record-audit.exe`; Windows/macOS have not been executed by this release's Linux CI.

## Contract

Binary plain dBASE III version03 only. Validate header/descriptor terminator, unique ASCII identifier field names, record width/count, deletion flags and optional single EOF byte. C,N,D,L fields only. Active and deleted rows have separate counts and numeric aggregates. Numeric values use exact decimal arithmetic; no exponents, commas, asterisk cleanup or silent rounding. Excess fractional digits, invalid calendar dates/logicals and character control bytes are findings. Blank and zero-date fields are missing. Character cells remain raw bytes: no codepage guessing or data conversion.

Report JSON goes to stdout. Exit0 means a valid report without documented findings, exit1 a valid report with findings, exit2 invalid/unsupported input or I/O failure with stderr and no partial report. This is a bounded read-only inspection tool; the optional example generator only creates an explicitly named new file.

## Limits

4 MiB,20000 records,128 fields,field names1..10 identifier characters. C width1..254; N width1..20 with decimals<=width-2; D8; L1. No memo/FoxPro/extensions, indexes, encoding conversion, table writes or business-metric interpretation. First512 cell findings identify row/field/reason without raw cell values; aggregates/field names can still be sensitive.

## Verify

```sh
python3 -m unittest -v test_behavior
python3 -m compileall -q .
python3 -m pip wheel --no-deps --wheel-dir dist .
python3 -m venv /tmp/dbf-record-audit-check
/tmp/dbf-record-audit-check/bin/python -m pip install --no-deps dist/*.whl
python3 verify_installed.py /tmp/dbf-record-audit-check/bin/python
```

Installed-command checks run outside the checkout. See [validation](VALIDATION.md), [research](RESEARCH.md), [contributing](CONTRIBUTING.md), [support](SUPPORT.md), [security](SECURITY.md) and [license](LICENSE).

Original implementation, prose and invented fixtures developed with AI assistance. MIT license. No verified production adoption or performance-superiority claim.
