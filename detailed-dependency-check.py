import zipfile
import os

def detailed_dependency_check():
    zip_path = "visitor-management-FINAL-with-pydantic-core.zip"
    
    print("🔍 DETAILED DEPENDENCY ANALYSIS")
    print("="*80)
    
    critical_deps = {
        'mangum': 'ASGI adapter for Lambda',
        'pydantic': 'Data validation',
        'pydantic_core': 'Pydantic core (CRITICAL)',
        'fastapi': 'Web framework', 
        'starlette': 'ASGI framework',
        'boto3': 'AWS SDK',
        'botocore': 'AWS core',
        'sqlalchemy': 'Database ORM',
        'typing_extensions': 'Type hints',
        'anyio': 'Async I/O',
        'h11': 'HTTP/1.1 protocol',
        'click': 'CLI framework',
        'uvicorn': 'ASGI server'
    }
    
    linux_indicators = [
        'linux',
        'x86_64', 
        'abi3',
        'cp3',
        'none'  # Platform independent
    ]
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            file_list = zip_file.namelist()
            
            print(f"📦 Total files: {len(file_list)}")
            print(f"📏 ZIP size: {os.path.getsize(zip_path):,} bytes\n")
            
            # Check each critical dependency
            print("🔍 CRITICAL DEPENDENCIES:")
            print("-" * 60)
            
            missing_deps = []
            for dep, description in critical_deps.items():
                # Find files related to this dependency
                dep_files = [f for f in file_list if dep.replace('_', '-') in f.lower() or dep.replace('-', '_') in f.lower()]
                
                if dep_files:
                    # Check if it's Linux compatible
                    linux_files = []
                    windows_files = []
                    
                    for f in dep_files:
                        if any(indicator in f.lower() for indicator in linux_indicators):
                            linux_files.append(f)
                        elif any(win_ind in f.lower() for win_ind in ['win32', 'win_amd64', '.exe', '.dll']):
                            windows_files.append(f)
                    
                    print(f"✅ {dep:<20} | {description}")
                    print(f"   📁 Files: {len(dep_files)}")
                    
                    if linux_files:
                        print(f"   🐧 Linux files: {len(linux_files)}")
                    if windows_files:
                        print(f"   🪟 Windows files: {len(windows_files)} ⚠️")
                    
                    # Show sample files
                    sample_files = dep_files[:3]
                    for sample in sample_files:
                        print(f"      • {sample}")
                    if len(dep_files) > 3:
                        print(f"      ... and {len(dep_files)-3} more")
                    print()
                else:
                    print(f"❌ {dep:<20} | {description} - MISSING!")
                    missing_deps.append(dep)
            
            # Check for platform-specific compiled files
            print("🔍 PLATFORM ANALYSIS:")
            print("-" * 60)
            
            compiled_files = [f for f in file_list if f.endswith(('.so', '.pyd', '.dll', '.dylib'))]
            wheel_files = [f for f in file_list if '.whl' in f]
            
            print(f"Binary files (.so/.pyd/.dll): {len(compiled_files)}")
            if compiled_files:
                for cf in compiled_files[:5]:
                    platform = "Linux" if cf.endswith('.so') else "Windows" if cf.endswith(('.pyd', '.dll')) else "Mac" 
                    print(f"   • {cf} ({platform})")
                if len(compiled_files) > 5:
                    print(f"   ... and {len(compiled_files)-5} more")
            
            print(f"\nWheel info files: {len(wheel_files)}")
            for wf in wheel_files[:3]:
                print(f"   • {wf}")
            
            # Final assessment
            print("\n" + "="*80)
            print("FINAL ASSESSMENT")
            print("="*80)
            
            if not missing_deps:
                print("✅ ALL CRITICAL DEPENDENCIES PRESENT")
            else:
                print(f"❌ MISSING DEPENDENCIES: {missing_deps}")
            
            if 'pydantic_core' not in [dep for dep in missing_deps]:
                print("✅ pydantic_core included (fixes original error)")
            else:
                print("❌ pydantic_core MISSING (will cause import error)")
            
            if any('linux' in f.lower() or f.endswith('.so') for f in file_list):
                print("✅ Linux-compatible dependencies detected")
            else:
                print("⚠️  No explicit Linux binaries found")
            
            # Check mangum specifically
            mangum_files = [f for f in file_list if 'mangum' in f.lower()]
            if mangum_files:
                print("✅ Mangum (Lambda adapter) present")
            else:
                print("❌ Mangum (Lambda adapter) MISSING")
                
            return len(missing_deps) == 0
            
    except Exception as e:
        print(f"❌ Error analyzing ZIP: {e}")
        return False

if __name__ == "__main__":
    success = detailed_dependency_check()
    print(f"\n🎯 READY FOR LAMBDA: {'✅ YES' if success else '❌ NO'}")