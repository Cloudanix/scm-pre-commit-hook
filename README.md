# scm-pre-commit-hook
**pre-commit-hook for scm**

**Code Scanning: Linux and MacOs**

**Secret Scanning: Linux, MacOs and Windows**

**Requires >=Python3.8**

* Sample .pre-commit-config:

```
repos:
-   repo: https://github.com/Cloudanix/scm-pre-commit-hook
    rev: 57bfb63
    hooks:
    -   id: cloudanix-scanner
        verbose: true
```
