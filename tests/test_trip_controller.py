#---------------------------------------------------
# File Name:   test_controller.py
# Description: Test suite for trip controller functionality.
#              Simple tests with real data from clean_train.csv.
# Author:      Janviere Munezero
# Date:        2025-10-15
#--------------------------------------------------- 

import sys
import os
import csv
from unittest.mock import Mock, patch

# Add the backend/app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app')))

from controllers.trip_controller import (
    get_all_trips,
    get_trips_by_vendor,
    get_trip,
    create_trip,
    delete_trip
)
from database.models import Trip


class TestTripController:
    """Simple tests for trip controller functionality"""

    def setup_method(self):
        """Set up test data"""
        # Load some real data from CSV for testing
        self.real_trips = self.load_real_data_sample()
        
        # Simple test trip
        self.test_trip = Trip(
            trip_id=1,
            vendor_id=1,
            pickup_datetime="2016-01-01T00:00:53+00:00",
            dropoff_datetime="2016-01-01T00:22:27+00:00",
            passenger_count=1,
            pickup_longitude=-73.985085,
            pickup_latitude=40.747166,
            dropoff_longitude=-73.958038,
            dropoff_latitude=40.717491,
            store_and_fwd_flag="N",
            trip_duration_sec=1294
        )
    
    def load_real_data_sample(self):
        """Load first 5 rows from clean_train.csv for testing"""
        try:
            csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'clean_train.csv')
            trips = []
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i >= 5:  # Only take first 5 rows
                        break
                    trip = Trip(
                        trip_id=i+1,
                        vendor_id=int(row['vendor_id']),
                        pickup_datetime=row['pickup_datetime'],
                        dropoff_datetime=row['dropoff_datetime'],
                        passenger_count=int(row['passenger_count']),
                        pickup_longitude=float(row['pickup_longitude']),
                        pickup_latitude=float(row['pickup_latitude']),
                        dropoff_longitude=float(row['dropoff_longitude']),
                        dropoff_latitude=float(row['dropoff_latitude']),
                        store_and_fwd_flag=row['store_and_fwd_flag'],
                        trip_duration_sec=int(float(row['trip_duration_sec']))
                    )
                    trips.append(trip)
            return trips
        except Exception as e:
            print(f"Could not load real data: {e}")
            return [self.test_trip]

    @patch('controllers.trip_controller.trip_manager')
    def test_get_all_trips(self, mock_trip_manager):
        """Test getting all trips"""
        # Setup mock to return our test data
        mock_trip_manager.get_trips.return_value = self.real_trips
        
        # Call the controller function
        result = get_all_trips(limit=10)
        
        # Check it returns the expected data
        assert result == self.real_trips
        mock_trip_manager.get_trips.assert_called_once_with(10)

    @patch('controllers.trip_controller.trip_manager')
    def test_get_trip_by_id(self, mock_trip_manager):
        """Test getting a single trip"""
        # Setup mock
        mock_trip_manager.get_trip_by_id.return_value = self.test_trip
        
        # Test the function
        result = get_trip(1)
        
        # Verify result
        assert result == self.test_trip
        assert result.trip_id == 1
        mock_trip_manager.get_trip_by_id.assert_called_once_with(1)

    @patch('controllers.trip_controller.trip_manager')
    def test_get_trips_by_vendor(self, mock_trip_manager):
        """Test getting trips for a specific vendor"""
        # Filter real trips for vendor_id = 1
        vendor_1_trips = [trip for trip in self.real_trips if trip.vendor_id == 1]
        mock_trip_manager.find_trips_by_vendor.return_value = vendor_1_trips
        
        # Test the function
        result = get_trips_by_vendor(1, limit=5)
        
        # Check results
        assert result == vendor_1_trips
        for trip in result:
            assert trip.vendor_id == 1

    @patch('controllers.trip_controller.validate_trip_data')
    @patch('controllers.trip_controller.trip_manager')
    def test_create_trip(self, mock_trip_manager, mock_validate):
        """Test creating a new trip"""
        # Setup mocks
        trip_data = {
            "vendor_id": 1,
            "pickup_datetime": "2016-01-01T00:00:00",
            "dropoff_datetime": "2016-01-01T01:00:00",
            "passenger_count": 2,
            "pickup_longitude": -73.9857,
            "pickup_latitude": 40.7484,
            "dropoff_longitude": -73.9857,
            "dropoff_latitude": 40.7584,
            "store_and_fwd_flag": "N",
            "trip_duration_sec": 3600
        }
        
        mock_validated_trip = Mock()
        mock_validated_trip.dict.return_value = trip_data
        mock_validate.return_value = mock_validated_trip
        mock_trip_manager.add_trip.return_value = 123
        
        # Test function
        result = create_trip(trip_data)
        
        # Verify
        assert result == 123
        mock_validate.assert_called_once_with(trip_data)

    @patch('controllers.trip_controller.trip_manager')
    def test_delete_trip(self, mock_trip_manager):
        """Test deleting a trip"""
        # Setup mock
        mock_trip_manager.delete_trip.return_value = True
        
        # Test function
        result = delete_trip(1)
        
        # Verify
        assert result is True
        mock_trip_manager.delete_trip.assert_called_once_with(1)
    
    def test_real_data_validation(self):
        """Test that our real CSV data is valid"""
        print(f"Testing {len(self.real_trips)} real trips from CSV...")
        
        for i, trip in enumerate(self.real_trips):
            # Basic data validation
            assert trip.passenger_count > 0, f"Trip {i}: passenger_count should be positive"
            assert trip.trip_duration_sec >= 0, f"Trip {i}: duration should be non-negative"
            assert trip.vendor_id > 0, f"Trip {i}: vendor_id should be positive"
            
            # NYC coordinate validation (rough bounds)
            assert -75.0 <= trip.pickup_longitude <= -73.0, f"Trip {i}: invalid pickup longitude"
            assert 40.0 <= trip.pickup_latitude <= 41.0, f"Trip {i}: invalid pickup latitude"
        
        print(f"All {len(self.real_trips)} real trips passed validation")


if __name__ == "__main__":
    # Simple test runner
    test = TestTripController()
    test.setup_method()
    
    # Run the real data validation test
    test.test_real_data_validation()
    print("Trip controller tests completed!")
