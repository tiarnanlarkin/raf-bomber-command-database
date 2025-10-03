# 🤖 AI Guide — RAF Bomber Command Database

Read `/docs/PREPRODUCTION.*` first.

**Workflow**
- Build/verify in local or Manus staging.
- Only working code lands on `main`.
- Tag releases (`vX.Y.Z`) when stable.

**Conventions**
- Conventional Commits.
- Run build/test/lint/type before push.

**Escalation**
If blocked: summarize → propose fix/rollback → wait for confirmation.

**Breadcrumbs**
- MACHINE_README.json (runtime/services/scripts)
- TASKS.md (live work)
- DECISIONS.md (ADRs)
- ONBOARDING.md (first 10 minutes)

**Golden Rule**
If PREPRODUCTION and `_meta` disagree, PREPRODUCTION is source-of-truth; sync `_meta`.
