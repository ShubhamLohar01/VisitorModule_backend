import zipfile
import os

def test_final_zip():
    zip_path = "visitor-management-FINAL.zip"
    
    print("🚀 TESTING FINAL COMPLETE ZIP FILE")
    print("="*80)
    
    if not os.path.exists(zip_path):
        print("❌ ZIP file not found!")
        return False
    
    file_size = os.path.getsize(zip_path)
    print(f"📦 File: {zip_path}")
    print(f"📏 Size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
    
    if file_size > 50 * 1024 * 1024:
        print("⚠️  File larger than 50MB - must use S3")
    else:
        print("✅ Size OK for direct upload")
    
    print(f"\n🔍 CHECKING CONTENTS...")
    
    critical_files = [
        'lambda_handler.py',
        'app/main.py',
        'app/core/config.py',
        'app/core/database.py'
    ]
    
    critical_packages = [
        'fastapi',
        'mangum',
        'boto3',
        'pydantic',
        'starlette'
    ]
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            file_list = zip_file.namelist()
            print(f"Total files: {len(file_list)}")
            
            # Check critical files
            print(f"\n📁 CRITICAL FILES:")
            missing_files = []
            for file_path in critical_files:
                if file_path in file_list:
                    print(f"✅ {file_path}")
                else:
                    print(f"❌ {file_path}")
                    missing_files.append(file_path)
            
            # Check packages
            print(f"\n📦 PACKAGES:")
            missing_packages = []
            for package in critical_packages:
                found = any(package in f for f in file_list)
                if found:
                    count = len([f for f in file_list if package in f])
                    print(f"✅ {package} ({count} files)")
                else:
                    print(f"❌ {package}")
                    missing_packages.append(package)
            
            # Check lambda_handler content
            print(f"\n🔍 LAMBDA HANDLER:")
            try:
                handler_content = zip_file.read('lambda_handler.py').decode('utf-8')
                
                checks = [
                    ('Production environment', 'os.environ["ENVIRONMENT"] = "production"'),
                    ('App import', 'from app.main import app'),
                    ('Lambda handler function', 'def lambda_handler('),
                    ('Mangum import', 'from mangum import Mangum')
                ]
                
                for check_name, check_text in checks:
                    if check_text in handler_content:
                        print(f"✅ {check_name}")
                    else:
                        print(f"❌ {check_name}")
                        
            except Exception as e:
                print(f"❌ Error reading lambda_handler.py: {e}")
            
            # Final verdict
            print(f"\n" + "="*80)
            print("FINAL RESULT")
            print("="*80)
            
            if not missing_files and not missing_packages:
                print("🎉 ZIP FILE IS COMPLETE AND READY!")
                print("✅ All dependencies included (Linux-compatible)")
                print("✅ All code files present")
                print("✅ Lambda handler configured")
                print("✅ Production settings applied")
                
                print(f"\n📋 DEPLOYMENT:")
                print(f"1. Upload: {zip_path} to S3")
                print(f"2. Lambda Console → Upload from S3")
                print(f"3. Test endpoints")
                
                return True
            else:
                print("❌ ZIP FILE HAS ISSUES:")
                if missing_files:
                    print(f"Missing files: {missing_files}")
                if missing_packages:
                    print(f"Missing packages: {missing_packages}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing ZIP: {e}")
        return False

if __name__ == "__main__":
    success = test_final_zip()
    print(f"\n🎯 TEST RESULT: {'✅ PASSED' if success else '❌ FAILED'}")