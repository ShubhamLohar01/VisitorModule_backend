import zipfile
import os
import sys

def test_lambda_deployment_zip(zip_path):
    """Test the Lambda deployment ZIP file for completeness"""
    
    print("🔍 TESTING LAMBDA DEPLOYMENT ZIP")
    print("="*60)
    print(f"ZIP File: {zip_path}")
    
    if not os.path.exists(zip_path):
        print("❌ ZIP file not found!")
        return False
    
    # Get file size
    file_size = os.path.getsize(zip_path)
    print(f"File Size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
    
    # Check if size is reasonable for Lambda (max 50MB for direct upload)
    if file_size > 50 * 1024 * 1024:
        print("⚠️  WARNING: File is larger than 50MB - must use S3 for deployment")
    else:
        print("✅ File size is acceptable for direct upload")
    
    print("\n" + "="*60)
    print("CHECKING ZIP CONTENTS")
    print("="*60)
    
    required_files = [
        'lambda_handler.py',
        'app/main.py',
        'app/core/config.py', 
        'app/core/database.py',
        'app/routers/visitor.py',
        'app/routers/approver.py'
    ]
    
    required_packages = [
        'fastapi',
        'mangum', 
        'boto3',
        'sqlalchemy',
        'pydantic',
        'uvicorn',
        'starlette'
    ]
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            file_list = zip_file.namelist()
            
            print(f"Total files in ZIP: {len(file_list)}")
            
            # Check required application files
            print("\n📁 APPLICATION FILES:")
            missing_files = []
            for file_path in required_files:
                if file_path in file_list:
                    print(f"✅ {file_path}")
                else:
                    print(f"❌ {file_path} - MISSING!")
                    missing_files.append(file_path)
            
            # Check required packages
            print("\n📦 REQUIRED PACKAGES:")
            missing_packages = []
            for package in required_packages:
                # Look for package directory or files
                package_found = any(package in f for f in file_list)
                if package_found:
                    # Find specific package files/directories
                    package_files = [f for f in file_list if package in f]
                    print(f"✅ {package} ({len(package_files)} files)")
                else:
                    print(f"❌ {package} - MISSING!")
                    missing_packages.append(package)
            
            # Check lambda_handler.py content
            print("\n🔍 LAMBDA HANDLER CHECK:")
            try:
                with zip_file.open('lambda_handler.py') as handler_file:
                    handler_content = handler_file.read().decode('utf-8')
                    
                    if 'os.environ["ENVIRONMENT"] = "production"' in handler_content:
                        print("✅ Production environment setting found")
                    else:
                        print("❌ Production environment setting missing")
                        
                    if 'from app.main import app' in handler_content:
                        print("✅ App import found")
                    else:
                        print("❌ App import missing")
                        
                    if 'def lambda_handler(' in handler_content:
                        print("✅ Lambda handler function found")
                    else:
                        print("❌ Lambda handler function missing")
                        
            except Exception as e:
                print(f"❌ Error reading lambda_handler.py: {e}")
            
            # Check main.py content
            print("\n🔍 MAIN.PY CHECK:")
            try:
                with zip_file.open('app/main.py') as main_file:
                    main_content = main_file.read().decode('utf-8')
                    
                    if 'docs_url = "/docs" if settings.ENVIRONMENT != "production" else None' in main_content:
                        print("✅ Production docs configuration found")
                    else:
                        print("❌ Production docs configuration missing")
                        
                    if 'def health_check():' in main_content:
                        print("✅ Health check endpoint found")
                    else:
                        print("❌ Health check endpoint missing")
                        
                    if 'try:' in main_content and 'except Exception as e:' in main_content:
                        print("✅ Error handling in health check found")
                    else:
                        print("❌ Error handling in health check missing")
                        
            except Exception as e:
                print(f"❌ Error reading app/main.py: {e}")
            
            print("\n" + "="*60)
            print("SUMMARY REPORT")
            print("="*60)
            
            if not missing_files and not missing_packages:
                print("🎉 ZIP FILE IS COMPLETE AND READY FOR DEPLOYMENT!")
                print("✅ All required files present")
                print("✅ All required packages present") 
                print("✅ Proper Lambda structure")
                
                print("\n📋 DEPLOYMENT INSTRUCTIONS:")
                print("1. Upload ZIP to S3 bucket")
                print("2. Go to Lambda Console → visitor-management-api")
                print("3. Code tab → Upload from → Amazon S3 location")
                print("4. Enter S3 URL and save")
                print("5. Test the endpoints")
                
                return True
            else:
                print("❌ ZIP FILE HAS ISSUES:")
                if missing_files:
                    print(f"   Missing files: {missing_files}")
                if missing_packages:
                    print(f"   Missing packages: {missing_packages}")
                return False
                
    except zipfile.BadZipFile:
        print("❌ Invalid or corrupted ZIP file")
        return False
    except Exception as e:
        print(f"❌ Error reading ZIP file: {e}")
        return False

# Test the ZIP file
zip_path = "visitor-management-api-complete.zip"
success = test_lambda_deployment_zip(zip_path)

print(f"\n🎯 TEST RESULT: {'PASSED' if success else 'FAILED'}")