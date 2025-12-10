#!/bin/bash

# ==========================================
# CONFIGURATION
# ==========================================
SOURCE_DIR=$(pwd)
# We assume the other repo is a sibling folder in /workspaces/
TARGET_REPO="../sandbox_luv"

# Files/Folders to KEEP in the current root (The VIP List)
# We use grep to match these, so be precise.
KEEP_PATTERN="README.md|LICENSE|Implementation Code|.git|.gitignore|.devcontainer|migrate_to_sandbox.sh"

# ==========================================
# VALIDATION
# ==========================================
echo "--------------------------------------------------"
echo "🧹 Housekeeping: Migrating loose files to Sandbox"
echo "--------------------------------------------------"
echo "SOURCE: $SOURCE_DIR"
echo "TARGET: $TARGET_REPO"

# 1. Check if the target repository folder exists
if [ ! -d "$TARGET_REPO" ]; then
    echo "⚠️  Target repository '$TARGET_REPO' not found!"
    echo "   Attempting to create it as a folder..."
    mkdir -p "$TARGET_REPO"
else
    echo "✅ Target repository found."
fi

# ==========================================
# EXECUTION
# ==========================================
echo ""
echo "Moving files..."

# 2. Loop through all files in the current directory
for item in * .[^.]*; do
    # Skip standard directory pointers
    if [[ "$item" == "." || "$item" == ".." ]]; then continue; fi

    # 3. Check if the item is in our KEEP list
    if echo "$item" | grep -E -q "^($KEEP_PATTERN)$"; then
        echo "   [KEPT] $item"
    else
        # 4. Move the item
        mv -f "$item" "$TARGET_REPO/"
        if [ $? -eq 0 ]; then
            echo "-> [MOVED] $item"
        else
            echo "!! [ERROR] Failed to move $item"
        fi
    fi
done

echo ""
echo "--------------------------------------------------"
echo "✅ Migration Complete!"
echo "Check your files in: $TARGET_REPO"
echo "--------------------------------------------------"
