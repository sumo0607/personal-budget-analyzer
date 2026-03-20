#!/usr/bin/env pwsh
# Hook: Inject project context at session start
# Returns a systemMessage with current project status

$frontendFiles = (Get-ChildItem -Recurse -File "frontend/src" -ErrorAction SilentlyContinue | Measure-Object).Count
$pythonFiles = (Get-ChildItem -Filter "*.py" -ErrorAction SilentlyContinue | Measure-Object).Count
$stitchFiles = (Get-ChildItem -Recurse -File "stitch" -Filter "*.html" -ErrorAction SilentlyContinue | Measure-Object).Count

$context = @{
    continue = $true
    systemMessage = @"
[Project Status]
- Frontend source files: $frontendFiles
- Legacy Python files: $pythonFiles  
- Stitch design templates: $stitchFiles
- Active work area: /frontend (Next.js 14 + TypeScript)
- Design ref: /stitch (HTML/Tailwind mockups)
- Specs: MIGRATION_TECH_SPEC.md, MIGRATION_DESIGN_SPEC.md, SPEC.md
"@
}

$context | ConvertTo-Json -Compress
