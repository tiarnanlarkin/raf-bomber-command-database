# GitHub Admin Setup (owner action)

UI:
1) Settings → Actions → Allow GitHub Actions.
2) Settings → Branches → Protect `main`:
   - Require status checks (meta-guard, build, test, lint, type)
   - Require linear history; block force-push.
3) Settings → Secrets → add required secrets (e.g., OPENAI_API_KEY).

CLI (optional):
- `bash scripts/gh_setup.sh owner/raf-bomber-command-database bomber-command flask react`
- Then: `gh secret set OPENAI_API_KEY -R owner/raf-bomber-command-database -b"$OPENAI_API_KEY"`

