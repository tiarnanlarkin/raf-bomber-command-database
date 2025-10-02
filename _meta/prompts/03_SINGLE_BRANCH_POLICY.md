# Single-Branch Policy

- Only `main` on GitHub; all work validated on Manus staging.
- Pre-push gate: build/test/lint/type (>=70% coverage). Abort on fail.
- Drift checks: staging == local == GitHub `main`.
- Tag releases; deploy from tags.
