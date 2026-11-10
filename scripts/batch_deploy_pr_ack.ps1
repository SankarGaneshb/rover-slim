$ErrorActionPreference = "Continue"
$owner = "SankarGaneshb"

$repos = @(
    @{ name = "Market-Rover"; branch = "main" },
    @{ name = "RoverID"; branch = "main" },
    @{ name = "Research_Rover"; branch = "main" },
    @{ name = "GoA_Rover"; branch = "main" },
    @{ name = "Portfolio-Tracker"; branch = "main" },
    @{ name = "linkedin-poll-scheduler"; branch = "main" },
    @{ name = "ElectionRover"; branch = "master" },
    @{ name = "Poll-Rover"; branch = "main" },
    @{ name = "BenefitsBridge"; branch = "main" },
    @{ name = "Reputation-Vault"; branch = "main" },
    @{ name = "StrikeGoal"; branch = "main" },
    @{ name = "Virtuoso"; branch = "main" },
    @{ name = "School-Bus-Connect"; branch = "main" },
    @{ name = "radis-app-main"; branch = "main" },
    @{ name = "gen-ai-bootcamp-2025"; branch = "main" }
)

$workflowPath = ".github/workflows/pr-acknowledgement.yml"
$content = Get-Content -Raw -Encoding UTF8 $workflowPath
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$b64 = [System.Convert]::ToBase64String($bytes)

$successCount = 0
$failCount = 0

foreach ($repo in $repos) {
    $repoName = $repo.name
    $branch = $repo.branch
    Write-Host "--> Deploying to $repoName ($branch)..."

    $sha = $null
    try {
        $existing = gh api "repos/$owner/$repoName/contents/$workflowPath?ref=$branch" 2>$null | ConvertFrom-Json
        if ($existing -and $existing.sha) {
            $sha = $existing.sha
        }
    } catch {}

    $bodyObj = @{
        message = "ci: add contributor PR acknowledgement workflow"
        content = $b64
        branch = $branch
    }
    if ($sha) {
        $bodyObj["sha"] = $sha
    }

    $jsonPayload = $bodyObj | ConvertTo-Json -Compress

    try {
        $null = $jsonPayload | gh api --method PUT "repos/$owner/$repoName/contents/$workflowPath" --input -
        Write-Host "    [SUCCESS] Deployed to $repoName"
        $successCount++
    } catch {
        Write-Host "    [FAILED] Failed to deploy to ${repoName}: $_"
        $failCount++
    }
}

Write-Host "Deployment completed: $successCount succeeded, $failCount failed."
