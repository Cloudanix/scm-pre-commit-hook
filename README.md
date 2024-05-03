# scm-pre-commit-hook
**pre-commit-hook for scm**

**Scanning works for: Linux:amd64 and MacOs:arm**

**Requires >=Python3.8**

* Sample .pre-commit-config:

```
repos:
-   repo: https://github.com/Cloudanix/scm-pre-commit-hook
    rev: b45d975
    hooks:
    -   id: cloudanix-scanner
        verbose: true
```
