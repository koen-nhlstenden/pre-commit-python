#!/bin/bash

docformatter --in-place --wrap-summaries 320 --wrap-descriptions 320 --make-summary-multi-line --pre-summary-newline "$@"

# Check if any files changed
if ! git diff --quiet -- "$@"; then
    echo "docformatter reformatted some files. Please stage the changes."
    git --no-pager diff -- "$@"
    exit 1
fi

exit 0
