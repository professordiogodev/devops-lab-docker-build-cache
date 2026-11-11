#!/usr/bin/env bash
rc=0
grep -q 'type=cache' Dockerfile.fast && echo "- ✅ Dockerfile.fast uses a pip cache mount" || { echo "- ❌ Dockerfile.fast has no RUN --mount=type=cache"; rc=1; }
grep -q 'data' .dockerignore && grep -q '.git' .dockerignore && echo "- ✅ .dockerignore ignores data and .git" || { echo "- ❌ .dockerignore must ignore data and .git"; rc=1; }
grep -qE '^ALL CHECKS PASSED \(' SUBMISSION.md && echo "- ✅ SUBMISSION.md shows ALL CHECKS PASSED" || { echo "- ❌ paste the verify.sh output ('ALL CHECKS PASSED') into SUBMISSION.md"; rc=1; }
exit $rc
