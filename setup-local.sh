#!/bin/bash
set -e

# =============================================================================
# Local Development Setup
# Creates venv and generates lockfiles for all environments
# =============================================================================

if ! command -v uv &> /dev/null; then
    echo "uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "Setting up local development environment..."

# Clean existing venv
[ -d ".venv" ] && rm -rf .venv

# Generate lockfiles for all environments (with latest versions)
echo "Generating lockfiles..."

# Local dev (full: backend + bot)
uv lock --upgrade
cp uv.lock uv.local.lock

# Lock a variant pyproject.toml in an isolated temp dir, so a failed or
# interrupted `uv lock` never leaves this repo's real pyproject.toml
# swapped out.
lock_variant() {
    local pyproject=$1
    local lockfile=$2
    local tmpdir
    tmpdir=$(mktemp -d)
    cp "$pyproject" "$tmpdir/pyproject.toml"
    (cd "$tmpdir" && uv lock --upgrade)
    mv "$tmpdir/uv.lock" "$lockfile"
    rm -rf "$tmpdir"
}

# API/Backend only
lock_variant pyproject.api.toml uv.api.lock

# Bot only
lock_variant pyproject.bot.toml uv.bot.lock

# Install local dev environment
echo "Installing dependencies..."
cp uv.local.lock uv.lock
uv sync
rm uv.lock

echo ""
echo "Done! Generated lockfiles:"
echo "  - uv.local.lock (local dev: backend + bot)"
echo "  - uv.api.lock   (backend deployment)"
echo "  - uv.bot.lock   (bot deployment)"
echo ""
echo "Run: source .venv/bin/activate"
