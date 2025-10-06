

### A) You already have the repo folder

Just update it instead of cloning:

```powershell
cd "$HOME\CLI_RESTART"
git remote set-url origin https://github.com/DICKY1987/CLI_RESTART.git
git fetch origin --prune
git checkout main
git pull --ff-only origin main
```

If you then want to merge `main` into your feature branch and push:

```powershell
$branch = 'feature/simplified-25ops-convo-updates'
git checkout $branch 2>$null || git checkout -t "origin/$branch" || git checkout -b $branch main
git merge --no-ff --no-edit main
if ($LASTEXITCODE -ne 0) {
  Write-Host "`nResolve conflicts, then:" -ForegroundColor Yellow
  Write-Host "  git add -A"
  Write-Host "  git commit --no-edit"
  Write-Host "  git push -u origin $branch"
} else {
  git push -u origin $branch
}
```

### B) A partial/failed clone left a folder you don’t want

Remove it and re-run the script:

```powershell
Remove-Item -Recurse -Force "$HOME\CLI_RESTART"
```

Then paste the one-paste script again (optionally set `-Branch 'feature/simplified-25ops-convo-updates'` in the `param(...)`).

---

### Optional: safer clone guard (drop-in change)

If you still want the single script to handle this gracefully, replace the **clone section** in your current script with this:

```powershell
# --- Clone if needed (robust) ---
$targetPath = Join-Path (Get-Location) $RepoName
if (Test-Path $targetPath) {
  if (Test-Path (Join-Path $targetPath '.git')) {
    Write-Host "→ Repo folder already exists; skipping clone." -ForegroundColor Yellow
  } else {
    throw "Folder '$targetPath' exists but is not a Git repo. Move/rename it or delete it, then re-run."
  }
} else {
  Write-Host "→ Cloning $RepoUrl ..." -ForegroundColor Green
  Exec "git clone `"$RepoUrl`" `"$RepoName`""
}
Set-Location -Path $targetPath
```

That will skip cloning if the repo directory already exists and has a `.git` folder, and fail fast (with a clear message) if a non-git folder is in the way.

If you hit another error, paste the **few lines above the red error** and I’ll zero in on it.
