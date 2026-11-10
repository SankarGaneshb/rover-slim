param(
    [string]$RepoName = "",
    [string]$Branch = "main",
    [switch]$All
)

$ErrorActionPreference = "Continue"
$owner = "SankarGaneshb"
$workflowPath = ".github/workflows/pr-acknowledgement.yml"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path "$scriptDir\.."
$fullWorkflowPath = Join-Path $repoRoot $workflowPath

if (-not (Test-Path $fullWorkflowPath)) {
    Write-Error "Workflow file not found at $fullWorkflowPath"
    exit 1
}

$content = Get-Content -Raw -Encoding UTF8 $fullWorkflowPath
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$b64 = [System.Convert]::ToBase64String($bytes)

function Deploy-WorkflowToRepo([string]$targetRepo, [string]$targetBranch) {
    Write-Host "--> Deploying to ${targetRepo} (${targetBranch})..."

    $sha = $null
    try {
        $existing = gh api "repos/$owner/$targetRepo/contents/$workflowPath?ref=$targetBranch" 2>$null | ConvertFrom-Json
        if ($existing -and $existing.sha) {
            $sha = $existing.sha
        }
    } catch {}

    $bodyObj = @{
        message = "ci: add contributor PR acknowledgement workflow"
        content = $b64
        branch = $targetBranch
    }
    if ($sha) {
        $bodyObj["sha"] = $sha
    }

    $jsonPayload = $bodyObj | ConvertTo-Json -Compress

    try {
        $null = $jsonPayload | gh api --method PUT "repos/$owner/$targetRepo/contents/$workflowPath" --input -
        Write-Host "    [SUCCESS] Deployed to $targetRepo"
        return $true
    } catch {
        Write-Host "    [FAILED] Failed to deploy to ${targetRepo}: $_"
        return $false
    }
}

if ($RepoName) {
    Deploy-WorkflowToRepo -targetRepo $RepoName -targetBranch $Branch
} elseif ($All -or (-not $RepoName)) {
    Write-Host "Discovering active non-fork repositories for $owner..."
    $reposJson = gh repo list $owner --limit 100 --source --no-archived --json name,defaultBranchRef | ConvertFrom-Json

    $successCount = 0
    $totalCount = 0

    foreach ($r in $reposJson) {
        $name = $r.name
        if ($name -eq $owner -or $name -eq "Hello-World") { continue }
        $br = if ($r.defaultBranchRef) { $r.defaultBranchRef.name } else { "main" }
        $totalCount++
        if (Deploy-WorkflowToRepo -targetRepo $name -targetBranch $br) {
            $successCount++
        }
    }
    Write-Host "`nCompleted: $successCount / $totalCount repositories updated."
}
