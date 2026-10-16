#!/usr/bin/env bash
# Builds the fixture post and checks the JS publisher rebuilds the same Wix payload.
set -e
cd "$(dirname "$0")/.."
python3 scripts/build_post.py tests/fixture --draft
node scripts/test_publish_js.js tests/fixture
python3 scripts/check_post.py tests/fixture >/dev/null || echo "(fixture is intentionally short: checker blocks it, as expected)"
