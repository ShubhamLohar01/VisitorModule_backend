#!/usr/bin/env python3
"""
Build Lambda Deployment Package with Linux Dependencies
Creates a deployment-ready zip file for AWS Lambda with proper Linux support
"""

import os
import sys
import shutil
import zipfile
import subprocess
from pathlib import Path
import tempfile

# Colors for terminal output
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GRAY = '\033[90m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

def print_header(msg):
    print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.CYAN}{msg}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def print_step(step, total, msg):
    print(f"{Colors.YELLOW}[{step}/{total}] {msg}{Colors.RESET}")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.WHITE}{msg}{Colors.RESET}")

def check_docker():
    """Check if Docker is available"""
    try:
        subprocess.run(['docker', '--version'], 
                      capture_output=True, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def build_with_docker(temp_dir, requirements_file):
    """Build dependencies using Docker for Linux compatibility"""
    print_info("Using Docker to build Linux-compatible dependencies...")
    
    # Create Dockerfile
    dockerfile_content = """FROM public.ecr.aws/lambda/python:3.11

WORKDIR /build

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt -t /build/packages

# Clean up unnecessary files
RUN find /build/packages -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
RUN find /build/packages -type f -name "*.pyc" -delete 2>/dev/null || true
RUN find /build/packages -type f -name "*.pyo" -delete 2>/dev/null || true
RUN find /build/packages -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
RUN find /build/packages -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
"""
    
    dockerfile_path = temp_dir / "Dockerfile.build"
    with open(dockerfile_path, 'w') as f:
        f.write(dockerfile_content)
    
    # Copy requirements to temp dir
    shutil.copy(requirements_file, temp_dir / "requirements.txt")
    
    try:
        # Build Docker image
        print_info("Building Docker image...")
        subprocess.run(
            ['docker', 'build', '-t', 'lambda-builder', 
             '-f', str(dockerfile_path), str(temp_dir)],
            check=True,
            capture_output=True
        )
        
        # Create container and extract packages
        print_info("Extracting packages...")
        subprocess.run(
            ['docker', 'create', '--name', 'lambda-builder-container', 'lambda-builder'],
            check=True,
            capture_output=True
        )
        
        packages_dir = temp_dir / "packages"
        packages_dir.mkdir(exist_ok=True)
        
        subprocess.run(
            ['docker', 'cp', 'lambda-builder-container:/build/packages/.', str(packages_dir)],
            check=True,
            capture_output=True
        )
        
        subprocess.run(
            ['docker', 'rm', 'lambda-builder-container'],
            check=True,
            capture_output=True
        )
        
        # Move packages to root of temp_dir
        for item in packages_dir.iterdir():
            shutil.move(str(item), str(temp_dir / item.name))
        packages_dir.rmdir()
        
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Docker build failed: {e}")
        return False

def build_with_pip(temp_dir, requirements_file):
    """Fallback: Build dependencies using pip with Linux platform target"""
    print_warning("Using pip with Linux platform target (may not be fully compatible)")
    print_info("For production, please use Docker for guaranteed Linux compatibility.")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install',
            '-r', str(requirements_file),
            '-t', str(temp_dir),
            '--upgrade',
            '--platform', 'manylinux2014_x86_64',
            '--only-binary=:all:',
            '--python-version', '311',
            '--implementation', 'cp'
        ], check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Pip install failed: {e}")
        print_error(e.stderr if e.stderr else "Unknown error")
        return False

def cleanup_package(temp_dir):
    """Remove unnecessary files to reduce package size"""
    print_info("Removing unnecessary files...")
    
    patterns_to_remove = [
        '**/___pycache__',
        '**/*.pyc',
        '**/*.pyo',
        '**/tests',
        '**/test',
        '**/*.dist-info/RECORD',
        '**/*.dist-info/INSTALLER',
        '**/*.dist-info/WHEEL',
    ]
    
    # Remove __pycache__ directories
    for pycache in temp_dir.rglob('__pycache__'):
        if pycache.is_dir():
            shutil.rmtree(pycache)
    
    # Remove .pyc and .pyo files
    for pyc in temp_dir.rglob('*.pyc'):
        pyc.unlink()
    for pyo in temp_dir.rglob('*.pyo'):
        pyo.unlink()
    
    # Remove test directories
    for test_dir in list(temp_dir.rglob('tests')) + list(temp_dir.rglob('test')):
        if test_dir.is_dir():
            shutil.rmtree(test_dir)
    
    # Clean up dist-info directories
    for dist_info in temp_dir.rglob('*.dist-info'):
        if dist_info.is_dir():
            for file in dist_info.iterdir():
                if file.name not in ['METADATA', 'top_level.txt']:
                    if file.is_dir():
                        shutil.rmtree(file)
                    else:
                        file.unlink()

def create_zip_package(temp_dir, output_zip):
    """Create the final zip package"""
    print_info("Creating zip archive...")
    
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(temp_dir)
                zipf.write(file_path, arcname)
    
    return output_zip

def get_directory_size(path):
    """Calculate total size of directory"""
    total = 0
    for entry in Path(path).rglob('*'):
        if entry.is_file():
            total += entry.stat().st_size
    return total

def main():
    print_header("Building Lambda Deployment Package (Linux)")
    
    # Configuration
    script_dir = Path(__file__).parent
    output_zip = script_dir / "lambda-deployment-linux.zip"
    
    # Step 1: Validate source files
    print_step(1, 6, "Validating source files...")
    
    required_files = ['app', 'lambda_handler.py', 'requirements.txt']
    missing_files = []
    
    for file in required_files:
        if not (script_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print_error(f"Missing required files: {', '.join(missing_files)}")
        return 1
    
    print_success("Source files validated")
    
    # Step 2: Create temporary build directory
    print_step(2, 6, "Creating build directory...")
    
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        
        # Copy application files
        print_info("Copying application code...")
        shutil.copytree(script_dir / 'app', temp_dir / 'app')
        shutil.copy(script_dir / 'lambda_handler.py', temp_dir)
        
        print_success("Application code copied")
        
        # Step 3: Install dependencies
        print_step(3, 6, "Installing Python dependencies for Linux...")
        
        has_docker = check_docker()
        
        if has_docker:
            print_info("Docker detected ✓")
            success = build_with_docker(temp_dir, script_dir / 'requirements.txt')
        else:
            print_warning("Docker not detected")
            success = build_with_pip(temp_dir, script_dir / 'requirements.txt')
        
        if not success:
            print_error("Dependency installation failed")
            return 1
        
        print_success("Dependencies installed")
        
        # Step 4: Clean up package
        print_step(4, 6, "Cleaning up unnecessary files...")
        cleanup_package(temp_dir)
        print_success("Cleanup complete")
        
        # Step 5: Create zip package
        print_step(5, 6, "Creating deployment package...")
        
        if output_zip.exists():
            output_zip.unlink()
        
        create_zip_package(temp_dir, output_zip)
        print_success(f"Package created: {output_zip.name}")
        
        # Step 6: Display package information
        print_step(6, 6, "Package Information")
        
        zip_size = output_zip.stat().st_size
        zip_size_mb = zip_size / (1024 * 1024)
        
        print_info(f"File: {output_zip.name}")
        print_info(f"Size: {zip_size_mb:.2f} MB")
        
        if zip_size_mb > 250:
            print_error("Package size exceeds Lambda limit (250MB)")
            print_error("You MUST use Lambda Layers for dependencies")
        elif zip_size_mb > 50:
            print_warning("Package size exceeds 50MB")
            print_warning("Consider using Lambda Layers for dependencies")
        else:
            print_success("Package size is within Lambda limits")
        
        print_info("\nContents:")
        dirs_shown = 0
        for item in sorted(temp_dir.iterdir()):
            if dirs_shown < 10:
                suffix = "/" if item.is_dir() else ""
                print(f"{Colors.GRAY}  - {item.name}{suffix}{Colors.RESET}")
                dirs_shown += 1
        
    # Final message
    print_header("Build Complete!")
    
    print(f"{Colors.YELLOW}Next Steps:{Colors.RESET}")
    print(f"{Colors.WHITE}1. Upload {output_zip.name} to AWS Lambda{Colors.RESET}")
    print(f"{Colors.WHITE}2. Set handler to: lambda_handler.lambda_handler{Colors.RESET}")
    print(f"{Colors.WHITE}3. Set runtime to: Python 3.11{Colors.RESET}")
    print(f"{Colors.WHITE}4. Configure environment variables{Colors.RESET}")
    print()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
