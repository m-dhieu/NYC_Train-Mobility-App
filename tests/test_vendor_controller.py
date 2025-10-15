#---------------------------------------------------
# File Name:   test_vendor_controller.py
# Description: Test suite for trip controller functionality.
#              Simple tests with real data from clean_train.csv.
# Author:      Janviere Munezero
# Date:        2025-10-15
#--------------------------------------------------- 

import sys
import os
import csv
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))

from controllers.vendor_controller import (
    get_all_vendors,
    get_vendor_by_id,
    create_vendor,
    update_vendor,
    delete_vendor
)
from database.models import Vendor


class TestVendorController:
    """Simple tests for vendor controller functionality"""

    def setup_method(self):
        """Set up test data"""
        # Load vendor info from real data
        self.real_vendor_ids = self.load_real_vendor_ids()
        
        # Simple test vendors
        self.test_vendors = [
            Vendor(vendor_id=1, vendor_name="Test Vendor 1"),
            Vendor(vendor_id=2, vendor_name="Test Vendor 2")
        ]
    
    def load_real_vendor_ids(self):
        """Load unique vendor IDs from clean_train.csv"""
        try:
            csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'clean_train.csv')
            vendor_ids = set()
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i >= 20:  # Only check first 20 rows
                        break
                    vendor_ids.add(int(row['vendor_id']))
            return sorted(list(vendor_ids))
        except Exception as e:
            print(f"Could not load real vendor data: {e}")
            return [1, 2]

    @patch('controllers.vendor_controller.vendor_manager')
    def test_get_all_vendors(self, mock_vendor_manager):
        """Test getting all vendors"""
        # Setup mock
        mock_vendor_manager.get_all_vendors.return_value = self.test_vendors
        
        # Test function
        result = get_all_vendors()
        
        # Verify
        assert result == self.test_vendors
        assert len(result) == 2
        mock_vendor_manager.get_all_vendors.assert_called_once()

    @patch('controllers.vendor_controller.vendor_manager')
    def test_get_vendor_by_id(self, mock_vendor_manager):
        """Test getting vendor by ID"""
        # Setup mock
        test_vendor = self.test_vendors[0]
        mock_vendor_manager.get_vendor_by_id.return_value = test_vendor
        
        # Test function
        result = get_vendor_by_id(1)
        
        # Verify
        assert result == test_vendor
        assert result.vendor_id == 1
        mock_vendor_manager.get_vendor_by_id.assert_called_once_with(1)

    @patch('controllers.vendor_controller.vendor_manager')
    def test_get_vendor_by_id_not_found(self, mock_vendor_manager):
        """Test getting vendor that doesn't exist"""
        # Setup mock
        mock_vendor_manager.get_vendor_by_id.return_value = None
        
        # Test function
        result = get_vendor_by_id(999)
        
        # Verify
        assert result is None
        mock_vendor_manager.get_vendor_by_id.assert_called_once_with(999)

    @patch('controllers.vendor_controller.vendor_manager')
    def test_create_vendor(self, mock_vendor_manager):
        """Test creating a new vendor"""
        # Setup mock
        vendor_name = "New Test Vendor"
        expected_id = 123
        mock_vendor_manager.add_vendor.return_value = expected_id
        
        # Test function
        result = create_vendor(vendor_name)
        
        # Verify
        assert result == expected_id
        mock_vendor_manager.add_vendor.assert_called_once_with(vendor_name)

    @patch('controllers.vendor_controller.vendor_manager')
    def test_update_vendor(self, mock_vendor_manager):
        """Test updating a vendor"""
        # Setup mock
        vendor_id = 1
        new_name = "Updated Vendor Name"
        original_vendor = self.test_vendors[0]
        updated_vendor = Vendor(vendor_id=vendor_id, vendor_name=new_name)
        
        mock_vendor_manager.get_vendor_by_id.side_effect = [original_vendor, updated_vendor]
        mock_vendor_manager.get_connection.return_value.__enter__.return_value = Mock()
        
        # Test function
        result = update_vendor(vendor_id, new_name)
        
        # Verify
        assert result == updated_vendor
        assert result.vendor_name == new_name

    @patch('controllers.vendor_controller.vendor_manager')
    def test_update_vendor_not_found(self, mock_vendor_manager):
        """Test updating vendor that doesn't exist"""
        # Setup mock
        mock_vendor_manager.get_vendor_by_id.return_value = None
        
        try:
            update_vendor(999, "Some Name")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Vendor not found" in str(e)

    @patch('controllers.vendor_controller.vendor_manager')
    def test_delete_vendor(self, mock_vendor_manager):
        """Test deleting a vendor"""
        # Setup mock
        mock_vendor_manager.delete_vendor.return_value = True
        
        # Test function
        result = delete_vendor(1)
        
        # Verify
        assert result is True
        mock_vendor_manager.delete_vendor.assert_called_once_with(1)

    @patch('controllers.vendor_controller.vendor_manager')
    def test_delete_vendor_not_found(self, mock_vendor_manager):
        """Test deleting vendor that doesn't exist"""
        # Setup mock
        mock_vendor_manager.delete_vendor.return_value = False
        
        # Test function
        result = delete_vendor(999)
        
        # Verify
        assert result is False
        mock_vendor_manager.delete_vendor.assert_called_once_with(999)

    def test_real_vendor_data_validation(self):
        """Test that real vendor IDs from CSV are valid"""
        print(f"Testing {len(self.real_vendor_ids)} real vendor IDs from CSV...")
        
        for vendor_id in self.real_vendor_ids:
            # Basic validation
            assert isinstance(vendor_id, int), f"Vendor ID should be integer: {vendor_id}"
            assert vendor_id > 0, f"Vendor ID should be positive: {vendor_id}"
        
        # Check we have reasonable number of vendors
        assert 1 <= len(self.real_vendor_ids) <= 10, f"Expected 1-10 vendors, got {len(self.real_vendor_ids)}"
        
        print(f"All {len(self.real_vendor_ids)} vendor IDs are valid: {self.real_vendor_ids}")


if __name__ == "__main__":
    # Simple test runner
    test = TestVendorController()
    test.setup_method()
    
    # Run the real data validation test
    test.test_real_vendor_data_validation()
    print("Vendor controller tests completed!")
