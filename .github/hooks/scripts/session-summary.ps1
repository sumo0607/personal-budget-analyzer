#!/usr/bin/env pwsh
# Hook: Stop — Log session summary with file change counts
# Appends to .github/session-log.md for tracking progress across sessions

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
$gitStatus = git diff --stat HEAD 2>$null
$changedCount = if ($gitStatus) { ($gitStatus | Measure-Object).Count - 1 } else { 0 }
$untrackedCount = (git ls-files --others --exclude-standard 2>$null | Measure-Object).Count

$logEntry = @"

## Session: $timestamp
- Files modified: $changedCount
- New untracked files: $untrackedCount
---
"@

$logPath = ".github/session-log.md"
if (-not (Test-Path $logPath)) {
    "# Session Log`n" | Set-Content $logPath
}
$logEntry | Add-Content $logPath

@{ continue = $true; systemMessage = "Session logged to $logPath" } | ConvertTo-Json -Compress
