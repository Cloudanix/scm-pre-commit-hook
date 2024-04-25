# scm-pre-commit-hook
**pre-commit-hook for scm**

**Linux Only**

**Requires >=Python3.8**

* Sample .pre-commit-config:

```
repos:
-   repo: https://github.com/Cloudanix/scm-pre-commit-hook
    rev: 14b49e9
    hooks:
    -   id: cloudanix-scanner
        verbose: true
```