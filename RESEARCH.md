# Research —18 October2026

User: Legacy GIS/data ingestion maintainers reviewing a small DBF before migration.

Pain: Silent float conversion, deletion filtering and cleanup can obscure malformed dates or decimal representations.

Smallest useful capability: Audit dBASE III binary table structure and active/deleted cell quality without coercing numeric data.

Acceptance: Exact0.1+0.2=.30, separate deleted rows, leap dates, invalid decimals/logicals, count/width/terminator errors, unsupported types and trailing byte rejection.

Demand is inferred from workflow and adjacent public discussions, not verified product requests. Discovery: descriptive GitHub topics, runnable invented example and chronological portfolio index. No unsolicited outreach or activity manipulation.

## Alternatives and evidence

Live GitHub repository search sorted Most stars: `DBF; spreadsheet parser plus documented reference follow`. Highest-star relevant comparable found in the inspected scope: **SheetJS/sheetjs**. Search and reference-follow coverage is limited, not an exhaustive global ranking. Unrelated keyword matches were excluded.

| Repository | Stars observed | Last push UTC | Archived | API license |
| --- | ---: | --- | --- | --- |
| [SheetJS/sheetjs](https://github.com/SheetJS/sheetjs) | 36343 | 2024-04-18T08:06:46Z | False | Apache-2.0 |
| [infused/dbf](https://github.com/infused/dbf) | 281 | 2026-10-16T02:05:00Z | False | MIT |
| [olemb/dbfread](https://github.com/olemb/dbfread) | 244 | 2024-07-24T20:10:58Z | False | MIT |
| [ethanfurman/dbf](https://github.com/ethanfurman/dbf) | 102 | 2025-09-15T16:28:42Z | False | NOASSERTION |
| [SheetJS/j](https://github.com/SheetJS/j) | 353 | 2017-12-05T07:24:11Z | True | NOASSERTION |

SheetJS is a broad spreadsheet conversion toolkit with DBF support; it was found by following the archived SheetJS/j project reference, not as the top result of the spreadsheet-parser query. SheetJS/j is archived historical context, not a maintained alternative. Dbfread already parses active/deleted records, and dbf/infused-dbf support broader DBF workflows. Selected dbfread parsing code informed our explicit refusal to coerce comma/asterisk representations. Historical date/precision issues are adjacent evidence, not verified demand for our product.

Current README, selected relevant source and up to five issue/PR records were read. [Provenance](RESEARCH_PROVENANCE.json) preserves exact URLs, observations and source identities. NOASSERTION is unclassified licensing, not permission to copy. No third-party implementation or fixtures are bundled.

Our narrow Python wheel has a clean-install example and failure contract. Established alternatives provide broader workflows, capabilities, documentation, examples and support communities. Competitor installs, time to first useful result, reliability, support response and technical performance were not measured. Our examples prove only our specified behavior. Stars inform discovery, not quality or performance. No feature-absence or superiority claim is made.

Portfolio distinction: No owned DBF binary table inspector was found among193 repositories. This is not another CSV/SQLite formatter: it validates dBASE descriptors, deletion semantics and fixed-width cell representation.

Standard formats and algorithms are not inventions of this project; the implementation/report interface and invented fixtures are original. No branding or competitor prose is copied. No technical performance benchmark was conducted.
