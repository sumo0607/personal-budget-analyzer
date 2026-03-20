#!/usr/bin/env pwsh
# Hook: PreToolUse — Ask confirmation before editing critical config files
# Receives JSON on stdin with toolName, toolInput.filePath

$input = $Input | Out-String
$data = $input | ConvertFrom-Json

$toolName = $data.toolName
$filePath = if ($data.toolInput.filePath) { $data.toolInput.filePath } else { "" }

$protectedFiles = @(
    'package.json',
    'package-lock.json',
    'tailwind.config.ts',
    'next.config.mjs',
    'tsconfig.json',
    '.env',
    '.env.local'
)

$isEditTool = $toolName -match 'edit|replace|create_file|write'
$isProtected = $false

foreach ($pf in $protectedFiles) {
    if ($filePath -like "*$pf") {
        $isProtected = $true
        break
    }
}

if ($isEditTool -and $isProtected) {
    $result = @{
        hookSpecificOutput = @{
            hookEventName = "PreToolUse"
            permissionDecision = "ask"
            permissionDecisionReason = "Protected config: $(Split-Path $filePath -Leaf). Confirm edit?"
        }
    }
} else {
    $result = @{ continue = $true }
}

$result | ConvertTo-Json -Depth 4 -Compress
