# HookPerfBenchMarking

HookPerfBenchMarking measures the end-to-end time required to scan synthetic
CLI hook payloads with Microsoft Defender. The project is intended to compare
hook scan performance across payload types, scanner invocation methods,
Defender releases, and endpoint configurations.

## Scope

The benchmark corpus includes synthetic hook payloads modeled after:

- Claude CLI prompt and tool hooks
- GitHub Copilot CLI hooks

The benchmark is designed to compare configurations such as:

| Dimension | Example configurations |
|---|---|
| Defender release | Pre-September release and later releases |
| Scanner invocation | PowerShell orchestration and direct executable invocation |
| Data Loss Prevention (DLP) | Enabled and disabled |
| Hook type | Prompt submission, pre-tool use, and post-tool use |
| Payload | Different tools, operations, and payload sizes |

Not every configuration in this matrix has been measured yet. Results should
identify the exact Defender version, invocation method, DLP state, payload
set, warm-up behavior, and number of runs used.

## Current benchmark

The initial Claude benchmark uses Defender platform version
`4.18.26080.3-0`, representing the pre-September Defender release. It compares:

1. A PowerShell wrapper that discovers and launches `DefenderAgentScan.exe`.
2. Direct invocation of `DefenderAgentScan.exe` without PowerShell
   orchestration.

For each payload, its complete file content is written to the scanner's
redirected standard input. Standard output and standard error are captured,
and total process duration is measured through process exit. One warm-up is
performed for each invocation method, followed by five alternating measured
runs. Per-payload results use the median duration.

## Repository layout

```text
HookPerfBenchMarking/
|-- Claude/
|   |-- hook_payloads/
|   |   |-- prompts/
|   |   `-- tools/
|   |-- run_defenderscan.ps1
|   |-- defender_scan_benchmark_report.md
|   |-- defender_scan_benchmark_summary.csv
|   `-- defender_scan_benchmark_raw.csv
`-- README.md
```

- `hook_payloads` contains the synthetic input corpus.
- `run_defenderscan.ps1` is the PowerShell orchestration path.
- `defender_scan_benchmark_report.md` contains the readable benchmark report.
- `defender_scan_benchmark_summary.csv` contains one summary row per payload.
- `defender_scan_benchmark_raw.csv` contains every measured invocation,
  including timing, exit code, and captured output.

Additional top-level directories can hold payloads and results for other CLI
clients, including GitHub Copilot CLI.

## Interpreting results

Process startup, scanner initialization, Defender state, system load, and
security policy can affect individual measurements. Compare medians from
repeated runs, retain raw measurements, and change only one configuration
dimension at a time. DLP-enabled and DLP-disabled runs should be performed on
otherwise equivalent systems and clearly labeled in their reports.
