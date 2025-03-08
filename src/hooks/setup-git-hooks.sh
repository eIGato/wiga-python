#!/usr/bin/env bash
set -ex

if [ -d .git ]; then
    GIT_DIR='.git'
else
    GIT_DIR=$(awk '{print $2}' .git)
fi
ln -s ../../src/hooks/pre-commit.sh "$GIT_DIR"/hooks/pre-commit.sh
mv "$GIT_DIR"/hooks/pre-commit.sh "$GIT_DIR"/hooks/pre-commit
