#!/bin/bash
# Proper yapf hook that works with pre-commit

files=("$@")
if [ ${#files[@]} -eq 0 ]; then
    echo "No files to format"
    exit 0
fi

# Format in place
yapf -i "${files[@]}"

# Check if yapf made any changes (dirty git state)
if ! git diff --quiet -- "${files[@]}"; then
    echo "Files were reformatted. Please re-stage them."
    git --no-pager diff -- "${files[@]}"
    exit 1
fi

exit 0
#!/bin/bash
# Proper yapf hook that works with pre-commit

files=("$@")
if [ ${#files[@]} -eq 0 ]; then
    echo "No files to format"
    exit 0
fi

# Format in place
yapf -i "${files[@]}"

# Check if yapf made any changes (dirty git state)
if ! git diff --quiet -- "${files[@]}"; then
    echo "Files were reformatted. Please re-stage them."
    git --no-pager diff -- "${files[@]}"
    exit 1
fi

exit 0
