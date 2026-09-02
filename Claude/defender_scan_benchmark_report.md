# Defender Hook Payload Benchmark

Generated: 2026-09-02 10:30:24 -07:00

## Methodology

- Payloads: 86 JSON hook payloads under hook_payloads\prompts and hook_payloads\tools.
- Input/output: payload content written to redirected stdin; stdout and stderr captured to completion.
- Runs: one unmeasured warm-up per invocation method, followed by five alternating measured runs per payload.
- Reported per-payload values: median of five end-to-end process durations.
- Direct executable: C:\Programdata\Microsoft\Windows Defender\Platform\4.18.26080.3-0\DefenderAgentScan.exe
- PowerShell wrapper: C:\HookPerfBenchMarking\Claude\run_defenderscan.ps1

## Overall Results

| Metric | Result |
|---|---:|
| Median direct time across payloads | 47.046 ms |
| Median wrapper time across payloads | 593.686 ms |
| Median wrapper overhead | 546.421 ms |
| Median wrapper/direct ratio | 12.66x |
| Measured process invocations | 860 |
| Non-zero exit codes | 0 |
| Runs with stdout/stderr output | 0 |

## Per-Payload Results

| Payload | Bytes | Direct median (ms) | Wrapper median (ms) | Overhead (ms) | Ratio |
|---|---:|---:|---:|---:|---:|
| prompts\01_UserPromptSubmit.json | 922 | 53.338 | 690.106 | 636.768 | 12.94x |
| prompts\02_UserPromptSubmit.json | 856 | 49.339 | 605.502 | 556.163 | 12.27x |
| prompts\03_UserPromptSubmit.json | 1190 | 51.742 | 618.181 | 566.439 | 11.95x |
| prompts\04_UserPromptSubmit.json | 763 | 57.274 | 714.991 | 657.717 | 12.48x |
| prompts\05_UserPromptSubmit.json | 953 | 48.294 | 600.585 | 552.291 | 12.44x |
| prompts\06_UserPromptSubmit.json | 1007 | 47.802 | 602.551 | 554.749 | 12.61x |
| prompts\07_UserPromptSubmit.json | 1626 | 50.139 | 611.252 | 561.113 | 12.19x |
| prompts\08_UserPromptSubmit.json | 924 | 45.181 | 581.291 | 536.11 | 12.87x |
| tools\Agent\PostToolUse.json | 1048 | 46.72 | 579.019 | 532.299 | 12.39x |
| tools\Agent\PreToolUse.json | 772 | 45.413 | 589.81 | 544.397 | 12.99x |
| tools\Artifact\PostToolUse.json | 1039 | 49.167 | 576.746 | 527.579 | 11.73x |
| tools\Artifact\PreToolUse.json | 830 | 44.627 | 579.085 | 534.458 | 12.98x |
| tools\AskUserQuestion\PostToolUse.json | 1993 | 44.81 | 568.27 | 523.46 | 12.68x |
| tools\AskUserQuestion\PreToolUse.json | 1731 | 42.522 | 579.684 | 537.162 | 13.63x |
| tools\CronCreate\PostToolUse.json | 829 | 41.636 | 571.828 | 530.192 | 13.73x |
| tools\CronCreate\PreToolUse.json | 676 | 41.636 | 582.785 | 541.149 | 14x |
| tools\CronDelete\PostToolUse.json | 629 | 44.595 | 584.112 | 539.517 | 13.1x |
| tools\CronDelete\PreToolUse.json | 529 | 43.662 | 575.074 | 531.412 | 13.17x |
| tools\CronList\PostToolUse.json | 1211 | 52.666 | 571.93 | 519.264 | 10.86x |
| tools\CronList\PreToolUse.json | 480 | 45.483 | 599.671 | 554.188 | 13.18x |
| tools\DesignSync\PostToolUse.json | 726 | 45.467 | 576.555 | 531.088 | 12.68x |
| tools\DesignSync\PreToolUse.json | 627 | 42.988 | 566.965 | 523.977 | 13.19x |
| tools\Edit\PostToolUse.json | 948 | 44.622 | 581.273 | 536.651 | 13.03x |
| tools\Edit\PreToolUse.json | 749 | 49.433 | 643.007 | 593.574 | 13.01x |
| tools\EndConversation\PostToolUse.json | 651 | 45.946 | 588.368 | 542.422 | 12.81x |
| tools\EndConversation\PreToolUse.json | 553 | 41.614 | 578.241 | 536.627 | 13.9x |
| tools\EnterPlanMode\PostToolUse.json | 585 | 46.735 | 573.458 | 526.723 | 12.27x |
| tools\EnterPlanMode\PreToolUse.json | 485 | 48.934 | 592.623 | 543.689 | 12.11x |
| tools\EnterWorktree\PostToolUse.json | 746 | 51.883 | 587.171 | 535.288 | 11.32x |
| tools\EnterWorktree\PreToolUse.json | 542 | 45.764 | 601.387 | 555.623 | 13.14x |
| tools\ExitPlanMode\PostToolUse.json | 761 | 48.144 | 607.302 | 559.158 | 12.61x |
| tools\ExitPlanMode\PreToolUse.json | 660 | 51.62 | 629.881 | 578.261 | 12.2x |
| tools\ExitWorktree\PostToolUse.json | 683 | 50.894 | 626.462 | 575.568 | 12.31x |
| tools\ExitWorktree\PreToolUse.json | 521 | 48.196 | 591.955 | 543.759 | 12.28x |
| tools\Glob\PostToolUse.json | 934 | 47.206 | 581.161 | 533.955 | 12.31x |
| tools\Glob\PreToolUse.json | 587 | 44.038 | 588.162 | 544.124 | 13.36x |
| tools\Grep\PostToolUse.json | 794 | 47.467 | 577.326 | 529.859 | 12.16x |
| tools\Grep\PreToolUse.json | 662 | 41.94 | 569.606 | 527.666 | 13.58x |
| tools\ListAgents\PostToolUse.json | 911 | 45.386 | 564.562 | 519.176 | 12.44x |
| tools\ListAgents\PreToolUse.json | 483 | 50.393 | 582.193 | 531.8 | 11.55x |
| tools\mcp__claude_ai_Gmail__authenticate\PostToolUse.json | 703 | 49.568 | 605.491 | 555.923 | 12.22x |
| tools\mcp__claude_ai_Gmail__authenticate\PreToolUse.json | 506 | 47.032 | 590.657 | 543.625 | 12.56x |
| tools\mcp__claude_ai_Gmail__complete_authentication\PostToolUse.json | 670 | 51.338 | 594.114 | 542.776 | 11.57x |
| tools\mcp__claude_ai_Gmail__complete_authentication\PreToolUse.json | 564 | 48.819 | 593.826 | 545.007 | 12.16x |
| tools\mcp__claude_ai_Google_Calendar__authenticate\PostToolUse.json | 624 | 45.081 | 577.089 | 532.008 | 12.8x |
| tools\mcp__claude_ai_Google_Calendar__authenticate\PreToolUse.json | 516 | 45.482 | 589.012 | 543.53 | 12.95x |
| tools\mcp__claude_ai_Google_Calendar__complete_authentication\PostToolUse.json | 680 | 44.267 | 582.73 | 538.463 | 13.16x |
| tools\mcp__claude_ai_Google_Calendar__complete_authentication\PreToolUse.json | 574 | 45.492 | 603.323 | 557.831 | 13.26x |
| tools\mcp__claude_ai_Google_Drive__authenticate\PostToolUse.json | 621 | 54.135 | 659.506 | 605.371 | 12.18x |
| tools\mcp__claude_ai_Google_Drive__authenticate\PreToolUse.json | 513 | 49.771 | 629.746 | 579.975 | 12.65x |
| tools\mcp__claude_ai_Google_Drive__complete_authentication\PostToolUse.json | 677 | 45.217 | 597.479 | 552.262 | 13.21x |
| tools\mcp__claude_ai_Google_Drive__complete_authentication\PreToolUse.json | 571 | 46.979 | 593.546 | 546.567 | 12.63x |
| tools\NotebookEdit\PostToolUse.json | 1017 | 44.386 | 592.971 | 548.585 | 13.36x |
| tools\NotebookEdit\PreToolUse.json | 917 | 46.877 | 595.025 | 548.148 | 12.69x |
| tools\PowerShell\PostToolUse.json | 933 | 43.823 | 585.614 | 541.791 | 13.36x |
| tools\PowerShell\PreToolUse.json | 644 | 48.754 | 596.317 | 547.563 | 12.23x |
| tools\PushNotification\PostToolUse.json | 715 | 46.302 | 598.205 | 551.903 | 12.92x |
| tools\PushNotification\PreToolUse.json | 618 | 44.98 | 598.819 | 553.839 | 13.31x |
| tools\Read\PostToolUse.json | 742 | 49.856 | 592.86 | 543.004 | 11.89x |
| tools\Read\PreToolUse.json | 566 | 53.632 | 624.923 | 571.291 | 11.65x |
| tools\RemoteTrigger\PostToolUse.json | 890 | 45.37 | 599.056 | 553.686 | 13.2x |
| tools\RemoteTrigger\PreToolUse.json | 736 | 52.54 | 609.661 | 557.121 | 11.6x |
| tools\ReportFindings\PostToolUse.json | 1414 | 46.106 | 591.73 | 545.624 | 12.83x |
| tools\ReportFindings\PreToolUse.json | 1313 | 48.155 | 594.431 | 546.276 | 12.34x |
| tools\ScheduleWakeup\PostToolUse.json | 930 | 46.758 | 599.765 | 553.007 | 12.83x |
| tools\ScheduleWakeup\PreToolUse.json | 764 | 49.433 | 596.913 | 547.48 | 12.08x |
| tools\SendFeedback\PostToolUse.json | 1036 | 52.423 | 632.306 | 579.883 | 12.06x |
| tools\SendFeedback\PreToolUse.json | 929 | 51.319 | 617.433 | 566.114 | 12.03x |
| tools\SendMessage\PostToolUse.json | 759 | 47.193 | 616.273 | 569.08 | 13.06x |
| tools\SendMessage\PreToolUse.json | 657 | 47.061 | 597.036 | 549.975 | 12.69x |
| tools\SendUserFile\PostToolUse.json | 747 | 48.734 | 608.149 | 559.415 | 12.48x |
| tools\SendUserFile\PreToolUse.json | 650 | 51.705 | 618.309 | 566.604 | 11.96x |
| tools\Skill\PostToolUse.json | 726 | 52.424 | 622.976 | 570.552 | 11.88x |
| tools\Skill\PreToolUse.json | 575 | 48.492 | 608.481 | 559.989 | 12.55x |
| tools\TaskOutput\PostToolUse.json | 703 | 47.788 | 599.462 | 551.674 | 12.54x |
| tools\TaskOutput\PreToolUse.json | 530 | 45.808 | 598.381 | 552.573 | 13.06x |
| tools\TaskStop\PostToolUse.json | 628 | 49.514 | 593.384 | 543.87 | 11.98x |
| tools\TaskStop\PreToolUse.json | 528 | 44.822 | 591.905 | 547.083 | 13.21x |
| tools\ToolSearch\PostToolUse.json | 845 | 45.76 | 599.523 | 553.763 | 13.1x |
| tools\ToolSearch\PreToolUse.json | 577 | 46.843 | 597.257 | 550.414 | 12.75x |
| tools\WebFetch\PostToolUse.json | 798 | 48.865 | 624.08 | 575.215 | 12.77x |
| tools\WebFetch\PreToolUse.json | 638 | 43.904 | 587.86 | 543.956 | 13.39x |
| tools\WebSearch\PostToolUse.json | 952 | 44.916 | 581.127 | 536.211 | 12.94x |
| tools\WebSearch\PreToolUse.json | 548 | 47.066 | 592.26 | 545.194 | 12.58x |
| tools\Write\PostToolUse.json | 838 | 48.124 | 593.345 | 545.221 | 12.33x |
| tools\Write\PreToolUse.json | 738 | 45.229 | 590.177 | 544.948 | 13.05x |
