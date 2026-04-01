#!/usr/bin/env python3
"""
Simple Lambda Deployment Package Builder
Creates a deployment-ready zip file for AWS Lambda without Docker dependency
"""

import os
import sys
import shutil
import zipfile
import subprocess
from pathlib import Path

def print_step(msg, level="INFO"):
    """Print formatted message"""
    colors = {
        "INFO": "\033[96m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m"
    }
    color = colors.get(level, colors["INFO"])
    reset = colors["RESET"]
    print(f"{color}{msg}{reset}")

def main():
    print_step("="*60, "INFO")
    print_step("Building Lambda Deployment Package", "INFO")
    print_step("="*60, "INFO")
    
    # Configuration
    script_dir = Path(__file__).parent
    output_zip = script_dir / "lambda-deployment-linux.zip"
    build_dir = script_dir / "lambda-build"
    
    # Step 1: Clean up
    print_step("\n[1/5] Cleaning up previous builds...", "INFO")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if output_zip.exists():
        output_zip.unlink()
    build_dir.mkdir()
    print_step("✓ Cleanup complete", "SUCCESS")
    
    # Step 2: Copy application code
    print_step("\n[2/5] Copying application code...", "INFO")
    
    # Copy app directory
    if (script_dir / "app").exists():
        shutil.copytree(script_dir / "app", build_dir / "app")
    else:
        print_step("ERROR: 'app' directory not found!", "ERROR")
        return 1
    
    # Copy lambda handler
    if (script_dir / "lambda_handler.py").exists():
        shutil.copy(script_dir / "lambda_handler.py", build_dir)
    else:
        print_step("ERROR: 'lambda_handler.py' not found!", "ERROR")
        return 1
    
    print_step("✓ Application code copied", "SUCCESS")
    
    # Step 3: Install dependencies
    print_step("\n[3/5] Installing dependencies for Linux...", "INFO")
    print_step("This may take several minutes...", "WARNING")
    
    requirements_file = script_dir / "requirements.txt"
    if not requirements_file.exists():
        print_step("ERROR: 'requirements.txt' not found!", "ERROR")
        return 1
    
    try:
        # Install with platform-specific wheels for Linux
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install',
            '-r', str(requirements_file),
            '-t', str(build_dir),
            '--upgrade',
            '--platform', 'manylinux2014_x86_64',
            '--only-binary=:all:',
            '--python-version', '311',
            '--implementation', 'cp',
            '--no-user'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            print_step("WARNING: Some packages may not have Linux wheels", "WARNING")
            print_step("Trying alternative installation method...", "WARNING")
            
            # Fallback: install without platform restriction
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install',
                '-r', str(requirements_file),
                '-t', str(build_dir),
                '--upgrade',
                '--no-user'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                print_step(f"ERROR: {result.stderr}", "ERROR")
                return 1
        
        print_step("✓ Dependencies installed", "SUCCESS")
        
    except subprocess.TimeoutExpired:
        print_step("ERROR: Installation timeout (>5 minutes)", "ERROR")
        return 1
    except Exception as e:
        print_step(f"ERROR: {str(e)}", "ERROR")
        return 1
    
    # Step 4: Clean up unnecessary files
    print_step("\n[4/5] Cleaning up unnecessary files...", "INFO")
    
    cleanup_count = 0
    
    # Remove __pycache__
    for pycache in build_dir.rglob('__pycache__'):
        shutil.rmtree(pycache)
        cleanup_count += 1
    
    # Remove .pyc files
    for pyc in build_dir.rglob('*.pyc'):
        pyc.unlink()
        cleanup_count += 1
    
    # Remove .pyo files
    for pyo in build_dir.rglob('*.pyo'):
        pyo.unlink()
        cleanup_count += 1
    
    # Remove test directories
    for test_dir in list(build_dir.rglob('tests')) + list(build_dir.rglob('test')):
        if test_dir.is_dir() and test_dir.parent.name != 'app':
            shutil.rmtree(test_dir)
            cleanup_count += 1
    
    # Slim down dist-info directories
    for dist_info in build_dir.rglob('*.dist-info'):
        if dist_info.is_dir():
            for file in list(dist_info.iterdir()):
                if file.name not in ['METADATA', 'top_level.txt', 'licenses']:
                    if file.is_dir():
                        shutil.rmtree(file)
                    else:
                        file.unlink()
                    cleanup_count += 1
    
    # Remove unnecessary egg-info
    for egg_info in build_dir.rglob('*.egg-info'):
        if egg_info.is_dir():
            shutil.rmtree(egg_info)
            cleanup_count += 1
    
    print_step(f"✓ Removed {cleanup_count} unnecessary items", "SUCCESS")
    
    # Step 5: Create zip file
    print_step("\n[5/5] Creating deployment package...", "INFO")
    
    try:
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(build_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(build_dir)
                    zipf.write(file_path, arcname)
        
        print_step(f"✓ Package created: {output_zip.name}", "SUCCESS")
        
    except Exception as e:
        print_step(f"ERROR creating zip: {str(e)}", "ERROR")
        return 1
    
    # Display package info
    print_step("\n" + "="*60, "INFO")
    print_step("Package Information", "INFO")
    print_step("="*60, "INFO")
    
    zip_size = output_zip.stat().st_size
    zip_size_mb = zip_size / (1024 * 1024)
    
    print_step(f"\nFile: {output_zip.name}", "INFO")
    print_step(f"Size: {zip_size_mb:.2f} MB", "INFO")
    
    if zip_size_mb > 250:
        print_step("\n⚠ Package exceeds 250MB - MUST use Lambda Layers!", "ERROR")
    elif zip_size_mb > 50:
        print_step("\n⚠ Package exceeds 50MB - Consider using S3 upload or Lambda Layers", "WARNING")
    else:
        print_step("\n✓ Package size is within Lambda limits", "SUCCESS")
    
    print_step("\nNext Steps:", "INFO")
    print_step("1. Upload to AWS Lambda", "INFO")
    print_step("2. Set handler: lambda_handler.lambda_handler", "INFO")
    print_step("3. Set runtime: Python 3.11", "INFO")
    print_step("4. Configure environment variables", "INFO")
    
    # Cleanup build directory
    print_step("\nCleaning up build directory...", "INFO")
    shutil.rmtree(build_dir)
    
    print_step("\n✓ Build Complete!\n", "SUCCESS")
    return 0

if __name__ == '__main__':
    sys.exit(main())
