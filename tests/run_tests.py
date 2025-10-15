#---------------------------------------------------
# File Name:   test_controller.py
# Description: Simple test runner for NYC taxi system.
#              Runs all tests and shows results.
# Author:      Janviere Munezero
# Date:        2025-10-15
#--------------------------------------------------- 


import sys
import os

def run_tests():
    """Run all our tests"""
    print("Running NYC Taxi System Tests...")

    # Test 1: Trip Controller
    print("\n1. Testing Trip Controller...")
    try:
        from test_trip_controller import TestTripController
        test = TestTripController()
        test.setup_method()
        test.test_real_data_validation()
        print("Trip controller tests passed")
    except Exception as e:
        print(f"Trip controller tests failed: {e}")
    
    # Test 2: Vendor Controller  
    print("\n2. Testing Vendor Controller...")
    try:
        from test_vendor_controller import TestVendorController
        test = TestVendorController()
        test.setup_method()
        test.test_real_vendor_data_validation()
        print("Vendor controller tests passed")
    except Exception as e:
        print(f"Vendor controller tests failed: {e}")
    
    # Test 3: Database
    print("\n3. Testing Database...")
    try:
        from test_database import TestDatabase
        test = TestDatabase()
        test.setup_method()
        try:
            test.test_database_connection()
            test.test_real_data_constraints()
            print("Database tests passed")
        finally:
            test.teardown_method()
    except Exception as e:
        print(f" Database tests failed: {e}")
    
    print("Test run completed!")

if __name__ == "__main__":
    run_tests()

if __name__ == "__main__":
    run_tests()
