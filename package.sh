#!/usr/bin/env bash
# Build the Canvas submission: dist/ADL-<StudentID>-project.zip
#
#   ./package.sh 2412345
#
# Contents = the committed files at HEAD (so .venv/, vector_store/, .env and the
# course brief never get in) + the demo videos, which are git-ignored.
# Prints warnings for anything that still looks unfinished.
set -euo pipefail

id="${1:?usage: ./package.sh <StudentID>}"
root="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
cd "$root"
name="ADL-${id}-project"
zip_path="$root/dist/$name.zip"

warn() { printf '  ! %s\n' "$*" >&2; }
echo "Checks:"

if ! git diff --quiet HEAD || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    warn "uncommitted changes are NOT included (only HEAD is packaged)"
fi
if grep -qE '\[(Your name|Student ID|repository URL)\]' report/report.md; then
    warn "report/report.md still has placeholders ([Your name] / [Student ID] / [repository URL])"
fi
if [ report/report.md -nt report/report.pdf ]; then
    warn "report.pdf is older than report.md - run report/build.sh and commit"
fi
shopt -s nullglob nocaseglob
videos=(demo_video/*.mp4 demo_video/*.mov demo_video/*.mkv demo_video/*.webm)
shopt -u nocaseglob
if [ "${#videos[@]}" -lt 4 ]; then
    warn "found ${#videos[@]} video(s) in demo_video/, expected 4 (or put Drive links in the report)"
fi

staging="$(mktemp -d)"
trap 'rm -rf "$staging"' EXIT
git archive --format=tar --prefix="$name/" HEAD | tar -x -C "$staging"
for v in "${videos[@]}"; do cp "$v" "$staging/$name/demo_video/"; done

mkdir -p "$root/dist"
rm -f "$zip_path"
(cd "$staging" && zip -qr -X "$zip_path" "$name")

echo
echo "Wrote $zip_path ($(du -h "$zip_path" | cut -f1))"
for d in source_code docker report demo_video; do
    [ -d "$staging/$name/$d" ] || warn "missing required folder $d/"
done
echo "Top level: $(ls "$staging/$name" | tr '\n' ' ')"
