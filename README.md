Use this pre-commit repo for consistent code style and formatting

To use, make a .pre-commit-config.yaml in the consuming repository with the following content:

```
repos:
  - repo: https://github.com/koen-nhlstenden/pre-commit-python
    rev: v0.1.1
    hooks:
      - id: yapf
      - id: docformatter
      - id: fix_docs
```

To use these pre-commits, make sure `docformatter` and `yapf` is installed.