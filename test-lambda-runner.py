"""
Lambda Test Runner
Simulates Lambda function execution with test events
"""

import json
import sys
import os

# Add the current directory to Python path to import lambda_handler
sys.path.append('.')

def run_test_case(test_file, description=""):
    """Run a single test case"""
    print(f"\n🔍 RUNNING TEST: {description or test_file}")
    print("="*60)
    
    try:
        # Read test event
        with open(test_file, 'r') as f:
            event = json.load(f)
        
        # Print test details
        method = event.get('httpMethod', 'UNKNOWN')
        path = event.get('path', 'UNKNOWN')
        print(f"Method: {method}")
        print(f"Path: {path}")
        
        if event.get('headers'):
            print(f"Headers: {len(event['headers'])} headers")
        
        if event.get('body'):
            print(f"Body: {event['body'][:100]}{'...' if len(event['body']) > 100 else ''}")
        
        print(f"\n📤 REQUEST:")
        print(f"   {method} {path}")
        
        # Import and run lambda handler
        try:
            from lambda_handler import lambda_handler
            
            # Create mock context
            class MockContext:
                def __init__(self):
                    self.function_name = "visitor-management-api"
                    self.function_version = "$LATEST"
                    self.invoked_function_arn = "arn:aws:lambda:ap-south-1:548830423226:function:visitor-management-api"
                    self.memory_limit_in_mb = "512"
                    self.remaining_time_in_millis = lambda: 30000
                    self.log_group_name = "/aws/lambda/visitor-management-api"
                    self.log_stream_name = "2026/01/14/[$LATEST]test123"
                    self.aws_request_id = "test-request-123"
            
            context = MockContext()
            
            # Execute lambda function
            print(f"\n📥 EXECUTING LAMBDA...")
            response = lambda_handler(event, context)
            
            # Print response
            print(f"\n📤 RESPONSE:")
            print(f"   Status: {response.get('statusCode', 'UNKNOWN')}")
            
            # Print headers
            if response.get('headers'):
                print(f"   Headers:")
                for key, value in response['headers'].items():
                    if 'cors' in key.lower() or 'access-control' in key.lower():
                        print(f"      {key}: {value}")
            
            # Print body
            if response.get('body'):
                try:
                    body = json.loads(response['body'])
                    print(f"   Body: {json.dumps(body, indent=2)}")
                except:
                    print(f"   Body: {response['body'][:200]}{'...' if len(response['body']) > 200 else ''}")
            
            # Status check
            status_code = response.get('statusCode', 0)
            if 200 <= status_code < 300:
                print(f"\n✅ TEST PASSED - Status {status_code}")
            elif 400 <= status_code < 500:
                print(f"\n⚠️  TEST WARNING - Status {status_code} (Client Error)")
            elif 500 <= status_code < 600:
                print(f"\n❌ TEST FAILED - Status {status_code} (Server Error)")
            else:
                print(f"\n❓ TEST UNKNOWN - Status {status_code}")
            
            return response
            
        except Exception as e:
            print(f"\n❌ LAMBDA EXECUTION ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
    except Exception as e:
        print(f"\n❌ TEST SETUP ERROR: {str(e)}")
        return None

def run_all_tests():
    """Run all test cases"""
    print("🚀 LAMBDA FUNCTION TEST SUITE")
    print("="*80)
    
    test_cases = [
        ("test-root-endpoint.json", "Root Endpoint (GET /)"),
        ("test-health-endpoint.json", "Health Check (GET /health)"),
        ("test-cors-preflight.json", "CORS Preflight (OPTIONS)")
    ]
    
    results = []
    
    for test_file, description in test_cases:
        if os.path.exists(test_file):
            response = run_test_case(test_file, description)
            status = response.get('statusCode', 0) if response else 0
            results.append((description, status, response is not None))
        else:
            print(f"\n❌ Test file not found: {test_file}")
            results.append((description, 0, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = 0
    total = len(results)
    
    for description, status, executed in results:
        if executed:
            if 200 <= status < 300:
                print(f"✅ {description} - Status {status}")
                passed += 1
            elif 400 <= status < 500:
                print(f"⚠️  {description} - Status {status}")
            else:
                print(f"❌ {description} - Status {status}")
        else:
            print(f"❌ {description} - Not executed")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Lambda function is working correctly!")
    elif passed > 0:
        print("⚠️  Some tests passed, check failed ones above")
    else:
        print("❌ All tests failed, check Lambda function deployment")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test case
        test_file = sys.argv[1]
        description = sys.argv[2] if len(sys.argv) > 2 else ""
        run_test_case(test_file, description)
    else:
        # Run all tests
        run_all_tests()