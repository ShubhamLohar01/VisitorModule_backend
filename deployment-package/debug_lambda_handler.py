import sys
import os

def lambda_handler(event, context):
    """Debug function to check Lambda environment"""
    
    result = []
    result.append("=== Lambda Environment Debug ===")
    result.append("")
    
    # Check Python version
    result.append(f"Python version: {sys.version}")
    result.append("")
    
    # Check Python path
    result.append("Python path:")
    for i, path in enumerate(sys.path):
        result.append(f"  {i}: {path}")
    result.append("")
    
    # Look for site-packages directories
    site_packages_dirs = [p for p in sys.path if 'site-packages' in p]
    result.append("Site-packages directories:")
    for sp in site_packages_dirs:
        result.append(f"  {sp}")
        if os.path.exists(sp):
            try:
                items = [item for item in os.listdir(sp) if 'mangum' in item.lower()]
                if items:
                    result.append(f"    Mangum-related items: {items}")
                else:
                    result.append("    No mangum found in this directory")
            except:
                result.append("    Could not list contents")
        else:
            result.append("    Directory does not exist")
    result.append("")
    
    # Try to import mangum
    result.append("Testing mangum import:")
    try:
        import mangum
        result.append("  ✅ SUCCESS: mangum imported successfully")
        result.append(f"  Version: {getattr(mangum, '__version__', 'unknown')}")
        result.append(f"  Location: {mangum.__file__}")
    except ImportError as e:
        result.append(f"  ❌ FAILED: {str(e)}")
    except Exception as e:
        result.append(f"  ❌ UNEXPECTED ERROR: {str(e)}")
    
    result.append("")
    result.append("=== End Debug Info ===")
    
    return {
        "statusCode": 200,
        "body": "\n".join(result)
    }