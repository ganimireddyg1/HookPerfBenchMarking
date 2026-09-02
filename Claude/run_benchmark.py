from __future__ import annotations

import argparse
import csv
import os
import statistics
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PAYLOAD_ROOT = SCRIPT_DIR / "hook_payloads"
DEFAULT_WRAPPER = SCRIPT_DIR / "run_defenderscan.ps1"


@dataclass(frozen=True)
class RunResult:
    payload: str
    method: str
    run: int
    milliseconds: float
    exit_code: int
    stdout_length: int
    stdout: str
    stderr_length: int
    stderr: str


@dataclass(frozen=True)
class PayloadSummary:
    payload: str
    bytes: int
    direct_median_ms: float | None
    wrapper_median_ms: float | None
    overhead_ms: float | None
    ratio: float | None
    direct_min_ms: float | None
    direct_max_ms: float | None
    wrapper_min_ms: float | None
    wrapper_max_ms: float | None
    all_exit_codes_zero: bool
    stdout_bytes: int
    stderr_bytes: int


def parse_args() -> argparse.Namespace:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    parser = argparse.ArgumentParser(
        description="Benchmark DefenderAgentScan against synthetic hook payloads."
    )
    parser.add_argument(
        "--payload-root",
        type=Path,
        default=DEFAULT_PAYLOAD_ROOT,
        help=f"Payload root (default: {DEFAULT_PAYLOAD_ROOT})",
    )
    parser.add_argument(
        "--payload",
        action="append",
        help=(
            "Payload path or glob relative to --payload-root; repeatable. "
            "Defaults to prompts/*.json and tools/**/*.json."
        ),
    )
    parser.add_argument(
        "--mode",
        choices=("both", "direct", "powershell"),
        default="both",
        help="Invocation method to benchmark (default: both).",
    )
    parser.add_argument(
        "--scanner",
        type=Path,
        help="Path to DefenderAgentScan.exe; auto-detected when omitted.",
    )
    parser.add_argument(
        "--wrapper",
        type=Path,
        default=DEFAULT_WRAPPER,
        help=f"PowerShell wrapper path (default: {DEFAULT_WRAPPER})",
    )
    parser.add_argument(
        "--powershell",
        default="powershell.exe",
        help="PowerShell executable name or path (default: powershell.exe).",
    )
    parser.add_argument(
        "--runs", type=positive_int, default=5, help="Measured runs per payload."
    )
    parser.add_argument(
        "--warmups",
        type=non_negative_int,
        default=1,
        help="Unmeasured warm-ups per invocation method.",
    )
    parser.add_argument(
        "--timeout",
        type=positive_float,
        default=120.0,
        help="Timeout in seconds for each scanner process (default: 120).",
    )
    parser.add_argument(
        "--defender-version",
        help="Defender version label for the report; inferred when omitted.",
    )
    parser.add_argument(
        "--dlp-state",
        choices=("on", "off", "unknown"),
        default="unknown",
        help="DLP configuration label recorded in the report.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=SCRIPT_DIR / f"defender_scan_benchmark_{timestamp}.md",
        help="Markdown report output path.",
    )
    parser.add_argument("--raw-csv", type=Path, help="Optional raw-run CSV path.")
    parser.add_argument(
        "--summary-csv", type=Path, help="Optional per-payload summary CSV path."
    )
    return parser.parse_args()


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def find_scanner(explicit_path: Path | None) -> Path:
    if explicit_path:
        scanner = explicit_path.expanduser().resolve()
        if not scanner.is_file():
            raise FileNotFoundError(f"Scanner not found: {scanner}")
        return scanner

    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows Defender"
        ) as key:
            install_location, _ = winreg.QueryValueEx(key, "InstallLocation")
        scanner = Path(install_location) / "DefenderAgentScan.exe"
        if scanner.is_file():
            return scanner.resolve()
    except (FileNotFoundError, OSError):
        pass

    platform_root = (
        Path(os.environ.get("ProgramData", r"C:\ProgramData"))
        / "Microsoft"
        / "Windows Defender"
        / "Platform"
    )
    candidates = sorted(
        platform_root.glob("*/DefenderAgentScan.exe"),
        key=lambda path: path.parent.name,
        reverse=True,
    )
    if candidates:
        return candidates[0].resolve()
    raise FileNotFoundError(
        "DefenderAgentScan.exe was not found. Supply its path with --scanner."
    )


def find_payloads(payload_root: Path, patterns: Sequence[str] | None) -> list[Path]:
    root = payload_root.expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Payload root not found: {root}")

    selected: set[Path] = set()
    if patterns:
        for pattern in patterns:
            candidate = Path(pattern).expanduser()
            if candidate.is_absolute():
                if not candidate.is_file():
                    raise FileNotFoundError(f"Payload not found: {candidate}")
                selected.add(candidate.resolve())
                continue
            matches = [path.resolve() for path in root.glob(pattern) if path.is_file()]
            if not matches:
                raise FileNotFoundError(f"Payload pattern matched no files: {pattern}")
            selected.update(matches)
    else:
        selected.update(path.resolve() for path in (root / "prompts").glob("*.json"))
        selected.update(path.resolve() for path in (root / "tools").glob("**/*.json"))

    payloads = sorted(selected, key=lambda path: str(path).lower())
    if not payloads:
        raise FileNotFoundError(f"No hook payload files found under {root}")
    return payloads


def command_for_method(
    method: str, scanner: Path, wrapper: Path, powershell: str
) -> list[str]:
    if method == "Direct executable":
        return [str(scanner)]
    if not wrapper.is_file():
        raise FileNotFoundError(f"PowerShell wrapper not found: {wrapper}")
    return [
        powershell,
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(wrapper),
    ]


def invoke(
    payload_name: str,
    payload: bytes,
    method: str,
    run: int,
    command: Sequence[str],
    timeout: float,
) -> RunResult:
    started = time.perf_counter_ns()
    completed = subprocess.run(
        command,
        input=payload,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    milliseconds = (time.perf_counter_ns() - started) / 1_000_000
    return RunResult(
        payload=payload_name,
        method=method,
        run=run,
        milliseconds=round(milliseconds, 3),
        exit_code=completed.returncode,
        stdout_length=len(completed.stdout),
        stdout=completed.stdout.decode("utf-8", errors="replace"),
        stderr_length=len(completed.stderr),
        stderr=completed.stderr.decode("utf-8", errors="replace"),
    )


def median_or_none(values: Sequence[float]) -> float | None:
    return round(statistics.median(values), 3) if values else None


def summarize(
    payloads: Sequence[Path], payload_root: Path, results: Sequence[RunResult]
) -> list[PayloadSummary]:
    summaries: list[PayloadSummary] = []
    for payload_path in payloads:
        payload_name = display_path(payload_path, payload_root)
        payload_results = [row for row in results if row.payload == payload_name]
        direct = sorted(
            row.milliseconds
            for row in payload_results
            if row.method == "Direct executable"
        )
        wrapper = sorted(
            row.milliseconds
            for row in payload_results
            if row.method == "PowerShell wrapper"
        )
        direct_median = median_or_none(direct)
        wrapper_median = median_or_none(wrapper)
        overhead = None
        ratio = None
        if direct_median is not None and wrapper_median is not None:
            overhead = round(wrapper_median - direct_median, 3)
            ratio = round(wrapper_median / direct_median, 2)
        summaries.append(
            PayloadSummary(
                payload=payload_name,
                bytes=len(payload_path.read_bytes()),
                direct_median_ms=direct_median,
                wrapper_median_ms=wrapper_median,
                overhead_ms=overhead,
                ratio=ratio,
                direct_min_ms=min(direct) if direct else None,
                direct_max_ms=max(direct) if direct else None,
                wrapper_min_ms=min(wrapper) if wrapper else None,
                wrapper_max_ms=max(wrapper) if wrapper else None,
                all_exit_codes_zero=all(
                    row.exit_code == 0 for row in payload_results
                ),
                stdout_bytes=sum(row.stdout_length for row in payload_results),
                stderr_bytes=sum(row.stderr_length for row in payload_results),
            )
        )
    return summaries


def display_path(path: Path, payload_root: Path) -> str:
    try:
        return str(path.relative_to(payload_root.resolve()))
    except ValueError:
        return str(path)


def format_value(value: float | None, suffix: str = "") -> str:
    return "N/A" if value is None else f"{value:.3f}{suffix}"


def markdown_report(
    args: argparse.Namespace,
    scanner: Path,
    payloads: Sequence[Path],
    results: Sequence[RunResult],
    summaries: Sequence[PayloadSummary],
) -> str:
    direct_medians = [
        row.direct_median_ms
        for row in summaries
        if row.direct_median_ms is not None
    ]
    wrapper_medians = [
        row.wrapper_median_ms
        for row in summaries
        if row.wrapper_median_ms is not None
    ]
    overheads = [row.overhead_ms for row in summaries if row.overhead_ms is not None]
    ratios = [row.ratio for row in summaries if row.ratio is not None]
    failures = sum(row.exit_code != 0 for row in results)
    output_runs = sum(
        row.stdout_length > 0 or row.stderr_length > 0 for row in results
    )
    version = args.defender_version or scanner.parent.name
    methods = {
        "both": "PowerShell wrapper and direct executable",
        "direct": "Direct executable",
        "powershell": "PowerShell wrapper",
    }

    lines = [
        "# Defender Hook Payload Benchmark",
        "",
        f"Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        "",
        "## Configuration",
        "",
        "| Setting | Value |",
        "|---|---|",
        f"| Payloads | {len(payloads)} |",
        f"| Invocation | {methods[args.mode]} |",
        f"| Defender version | {escape_cell(version)} |",
        f"| Scanner | `{scanner}` |",
        f"| DLP state | {args.dlp_state} |",
        f"| Warm-ups per method | {args.warmups} |",
        f"| Measured runs per payload and method | {args.runs} |",
        f"| Process timeout | {args.timeout:g} seconds |",
        "",
        "Payload bytes were written to redirected standard input. Standard output",
        "and standard error were captured through process exit. Per-payload values",
        "are medians of the measured end-to-end process durations.",
        "",
        "## Overall Results",
        "",
        "| Metric | Result |",
        "|---|---:|",
    ]
    if direct_medians:
        lines.append(
            "| Median direct time across payloads | "
            f"{statistics.median(direct_medians):.3f} ms |"
        )
    if wrapper_medians:
        lines.append(
            "| Median wrapper time across payloads | "
            f"{statistics.median(wrapper_medians):.3f} ms |"
        )
    if overheads:
        lines.append(
            f"| Median wrapper overhead | {statistics.median(overheads):.3f} ms |"
        )
    if ratios:
        lines.append(
            f"| Median wrapper/direct ratio | {statistics.median(ratios):.2f}x |"
        )
    lines.extend(
        [
            f"| Measured process invocations | {len(results)} |",
            f"| Non-zero exit codes | {failures} |",
            f"| Runs with stdout/stderr output | {output_runs} |",
            "",
            "## Per-Payload Results",
            "",
        ]
    )

    if args.mode == "both":
        lines.extend(
            [
                "| Payload | Bytes | Direct median (ms) | Wrapper median (ms) "
                "| Overhead (ms) | Ratio |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for row in summaries:
            lines.append(
                f"| {escape_cell(row.payload)} | {row.bytes} "
                f"| {format_value(row.direct_median_ms)} "
                f"| {format_value(row.wrapper_median_ms)} "
                f"| {format_value(row.overhead_ms)} "
                f"| {format_value(row.ratio, 'x')} |"
            )
    else:
        direct_mode = args.mode == "direct"
        lines.extend(
            [
                "| Payload | Bytes | Median (ms) | Min (ms) | Max (ms) |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for row in summaries:
            median = row.direct_median_ms if direct_mode else row.wrapper_median_ms
            minimum = row.direct_min_ms if direct_mode else row.wrapper_min_ms
            maximum = row.direct_max_ms if direct_mode else row.wrapper_max_ms
            lines.append(
                f"| {escape_cell(row.payload)} | {row.bytes} "
                f"| {format_value(median)} | {format_value(minimum)} "
                f"| {format_value(maximum)} |"
            )

    if output_runs:
        lines.extend(
            [
                "",
                "## Captured Output",
                "",
                "One or more runs produced output. Use `--raw-csv` to retain the exact",
                "stdout and stderr content for each invocation.",
            ]
        )
    return "\n".join(lines) + "\n"


def escape_cell(value: object) -> str:
    return str(value).replace("|", r"\|").replace("\r", " ").replace("\n", " ")


def write_csv(path: Path, rows: Sequence[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    dictionaries = [asdict(row) for row in rows]
    if not dictionaries:
        raise ValueError(f"Cannot write an empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=dictionaries[0].keys())
        writer.writeheader()
        writer.writerows(dictionaries)


def main() -> int:
    args = parse_args()
    payload_root = args.payload_root.expanduser().resolve()
    payloads = find_payloads(payload_root, args.payload)
    scanner = find_scanner(args.scanner)
    wrapper = args.wrapper.expanduser().resolve()
    methods = {
        "both": ("PowerShell wrapper", "Direct executable"),
        "direct": ("Direct executable",),
        "powershell": ("PowerShell wrapper",),
    }[args.mode]
    commands = {
        method: command_for_method(method, scanner, wrapper, args.powershell)
        for method in methods
    }

    warm_payload = payloads[0].read_bytes()
    warm_name = display_path(payloads[0], payload_root)
    for method in methods:
        for warmup in range(1, args.warmups + 1):
            print(f"Warm-up {warmup}/{args.warmups}: {method}", flush=True)
            invoke(
                warm_name,
                warm_payload,
                method,
                0,
                commands[method],
                args.timeout,
            )

    results: list[RunResult] = []
    for index, payload_path in enumerate(payloads, start=1):
        payload_name = display_path(payload_path, payload_root)
        payload = payload_path.read_bytes()
        print(f"[{index}/{len(payloads)}] {payload_name}", flush=True)
        for run in range(1, args.runs + 1):
            for method in methods:
                result = invoke(
                    payload_name,
                    payload,
                    method,
                    run,
                    commands[method],
                    args.timeout,
                )
                results.append(result)
                if result.stdout:
                    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")

    summaries = summarize(payloads, payload_root, results)
    report_path = args.report.expanduser().resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        markdown_report(args, scanner, payloads, results, summaries),
        encoding="utf-8",
        newline="\n",
    )
    if args.raw_csv:
        write_csv(args.raw_csv.expanduser().resolve(), results)
    if args.summary_csv:
        write_csv(args.summary_csv.expanduser().resolve(), summaries)

    failures = sum(result.exit_code != 0 for result in results)
    print(f"Report: {report_path}")
    print(f"Payloads: {len(payloads)}; invocations: {len(results)}; failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
