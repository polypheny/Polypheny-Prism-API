#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 || ! "$1" =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]]; then
    echo "Usage: $0 <major.minor> <output-directory>" >&2
    exit 2
fi

mkdir -p "$2"
output_dir="$(cd "$2" && pwd)"
if [[ -e "$output_dir/prism" ]]; then
    echo "Output directory already contains a prism package: $output_dir" >&2
    exit 2
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
generated="$(mktemp -d)"
trap 'rm -rf "$generated"' EXIT

cd "$repo_root"
protoc -I . --go_out="$generated" --go_opt=paths=source_relative org/polypheny/prism/*.proto

IFS=. read -r major minor <<< "$1"
cat > "$generated/org/polypheny/prism/version.go" <<EOF
package prism

// MajorVersion is the major component of the API version.
const MajorVersion = $major

// MinorVersion is the minor component of the API version.
const MinorVersion = $minor
EOF

mv "$generated/org/polypheny/prism" "$output_dir/prism"
