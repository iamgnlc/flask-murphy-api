#!/bin/bash
PATTERN="(/__pycache__$|.pytest_cache|.ruff_cache|\.pyc$|\.pyo$)"
find . | grep -E $PATTERN | xargs rm -rf
