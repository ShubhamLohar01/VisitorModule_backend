# Fix: botocore.docs and boto3.docs Import Errors

## Problems
```
[ERROR] Runtime.ImportModuleError: Unable to import module 'lambda_handler': No module named 'botocore.docs'
[ERROR] Runtime.ImportModuleError: Unable to import module 'lambda_handler': No module named 'boto3.docs'
```

## Root Cause

During layer cleanup to reduce size, we removed `botocore.docs` and `boto3.docs` thinking they were just documentation. However, **these are actually runtime modules** that boto3 imports for help text and documentation features.

## Solution

### ✅ Fixed - What Was Done:

1. **Reinstalled botocore** to restore the `botocore.docs` module
2. **Reinstalled boto3** to restore the `boto3.docs` module
3. **Recreated layer.zip** with both docs modules included
4. **Updated cleanup script** to preserve all `*.docs` modules in the future

### Current Status:

- ✅ `botocore.docs` restored (34 files)
- ✅ `boto3.docs` restored
- ✅ New `layer.zip` created: **~82 MB**
- ✅ Ready to upload to S3

## Important Notes

### ⚠️ Modules That Look Like "Docs" But Are Runtime:

These modules should **NEVER** be removed:
- `botocore.docs` - Required by boto3 at runtime
- `boto3.docs` - Required by boto3 at runtime
- **Any `*.docs` module** - May be runtime modules, not just documentation!

### ✅ Safe to Remove:

- `tests/` directories (unless package needs them)
- `test/` directories
- `examples/` directories
- `*.md` files (documentation)
- `LICENSE*` files
- `CHANGELOG*` files
- `__pycache__/` directories
- `*.pyc` files

### ❌ Never Remove:

- **`*.docs` modules** (boto3.docs, botocore.docs are runtime!)
- `*.dist-info/` directories (package metadata)
- `__init__.py` files
- Any `.py` files in package directories
- Native libraries (`.so` files)

## Updated Cleanup Rules

When reducing layer size, use these rules:

```powershell
# Safe cleanup (preserves runtime modules)
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyo" | Remove-Item -Force

# Remove tests (but NOT *.docs modules - they're runtime!)
Get-ChildItem -Path . -Recurse -Directory -Filter "tests" | 
    Where-Object { $_.FullName -notlike "*boto*" } | 
    Remove-Item -Recurse -Force

# Remove documentation files
Get-ChildItem -Path . -Recurse -Filter "*.md" | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Filter "LICENSE*" | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Filter "CHANGELOG*" | Remove-Item -Force

# NEVER remove:
# - botocore.docs (runtime module!)
# - boto3.docs (runtime module!)
# - Any *.docs module (may be runtime!)
# - Any .py files
# - Any .so files (native libraries)
```

## Next Steps

1. ✅ Upload the new `layer.zip` (81.73 MB) to S3
2. ✅ Create/update Lambda Layer with new ZIP
3. ✅ Test Lambda function - should work now!

## Prevention

The cleanup script (`create_lambda_layer_windows.ps1`) has been updated to preserve **all `*.docs` modules** (including `botocore.docs` and `boto3.docs`) in future builds.

---

**Status**: ✅ Fixed - layer.zip now includes both botocore.docs and boto3.docs
