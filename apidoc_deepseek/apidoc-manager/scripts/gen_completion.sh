#!/bin/bash
set -e

OUTPUT_DIR="${1:-completions}"
mkdir -p "$OUTPUT_DIR"

echo "Generating shell completions in $OUTPUT_DIR..."
apidoc --show-completion bash > "$OUTPUT_DIR/apidoc.bash" && echo "✓ Bash"
apidoc --show-completion zsh > "$OUTPUT_DIR/apidoc.zsh" && echo "✓ Zsh"
apidoc --show-completion fish > "$OUTPUT_DIR/apidoc.fish" && echo "✓ Fish"
echo ""
echo "Done! To install:"
echo "Bash:  source $OUTPUT_DIR/apidoc.bash"
echo "Zsh:   source $OUTPUT_DIR/apidoc.zsh"
echo "Fish:  cp $OUTPUT_DIR/apidoc.fish ~/.config/fish/completions/"
