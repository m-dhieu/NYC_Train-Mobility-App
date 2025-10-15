#---------------------------------------------------
# File Name:   test_database.py
# Description: Simple database tests for NYC taxi data system.
#              Tests basic database operations and real data validation.
#  Author:      Janviere Munezero
# Date:        2025-10-15
#--------------------------------------------------- 

import sys
import os
import csv
import sqlite3
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))



class TestDatabase:
    """Simple tests for database functionality"""

    def setup_method(self):
        """Set up test database"""
        # Create temporary database for testing
        self.test_db_path = tempfile.mktemp(suffix='.db')
        self.create_test_database()
        
        # Load some real data for testing
        self.real_trips = self.load_real_data_sample()

    def teardown_method(self):
        """Clean up test database"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def create_test_database(self):
        """Create test database with proper schema"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Create Vendors table
        cursor.execute("""
            CREATE TABLE Vendors (
                vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_name TEXT NOT NULL
            )
        """)
        
        # Create Trips table
        cursor.execute("""
            CREATE TABLE Trips (
                trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_id INTEGER NOT NULL,
                pickup_datetime TEXT NOT NULL,
                dropoff_datetime TEXT NOT NULL,
                passenger_count INTEGER NOT NULL CHECK(passenger_count > 0),
                pickup_longitude REAL NOT NULL,
                pickup_latitude REAL NOT NULL,
                dropoff_longitude REAL NOT NULL,
                dropoff_latitude REAL NOT NULL,
                store_and_fwd_flag TEXT,
                trip_duration_sec INTEGER NOT NULL CHECK(trip_duration_sec >= 0),
                FOREIGN KEY (vendor_id) REFERENCES Vendors(vendor_id)
            )
        """)
        
        conn.commit()
        conn.close()

    def load_real_data_sample(self):
        """Load first 3 trips from clean_train.csv"""
        try:
            csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'clean_train.csv')
            trips = []
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i >= 3:  # Only take first 3 rows for simple testing
                        break
                    trip = {
                        'vendor_id': int(row['vendor_id']),
                        'pickup_datetime': row['pickup_datetime'],
                        'dropoff_datetime': row['dropoff_datetime'],
                        'passenger_count': int(row['passenger_count']),
                        'pickup_longitude': float(row['pickup_longitude']),
                        'pickup_latitude': float(row['pickup_latitude']),
                        'dropoff_longitude': float(row['dropoff_longitude']),
                        'dropoff_latitude': float(row['dropoff_latitude']),
                        'store_and_fwd_flag': row['store_and_fwd_flag'],
                        'trip_duration_sec': int(float(row['trip_duration_sec']))
                    }
                    trips.append(trip)
            return trips
        except Exception as e:
            print(f"Could not load real data: {e}")
            return []

    def test_database_connection(self):
        """Test that we can connect to database"""
        conn = sqlite3.connect(self.test_db_path)
        
        # Check tables exist
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'Vendors' in tables, "Vendors table should exist"
        assert 'Trips' in tables, "Trips table should exist"
        
        conn.close()
        print("Database connection test passed")

    def test_vendor_operations(self):
        """Test basic vendor database operations"""
        conn = sqlite3.connect(self.test_db_path)
        
        # Insert test vendor
        cursor = conn.execute("INSERT INTO Vendors (vendor_name) VALUES (?)", ("Test Vendor",))
        vendor_id = cursor.lastrowid
        conn.commit()
        
        assert vendor_id is not None, "Should get vendor ID after insert"
        assert vendor_id > 0, "Vendor ID should be positive"
        
        # Retrieve vendor
        cursor = conn.execute("SELECT vendor_id, vendor_name FROM Vendors WHERE vendor_id = ?", (vendor_id,))
        row = cursor.fetchone()
        
        assert row is not None, "Should be able to retrieve inserted vendor"
        assert row[0] == vendor_id, "Retrieved vendor ID should match"
        assert row[1] == "Test Vendor", "Retrieved vendor name should match"
        
        # Delete vendor
        cursor = conn.execute("DELETE FROM Vendors WHERE vendor_id = ?", (vendor_id,))
        rows_deleted = cursor.rowcount
        conn.commit()
        
        assert rows_deleted == 1, "Should delete exactly one row"
        
        conn.close()
        print("Vendor operations test passed")

    def test_trip_operations_with_real_data(self):
        """Test trip operations using real data"""
        if not self.real_trips:
            print("No real data available, skipping test")
            return
            
        conn = sqlite3.connect(self.test_db_path)
        
        # First, create vendors for our trips
        vendors_created = set()
        for trip in self.real_trips:
            vendor_id = trip['vendor_id']
            if vendor_id not in vendors_created:
                conn.execute("INSERT OR IGNORE INTO Vendors (vendor_id, vendor_name) VALUES (?, ?)", 
                           (vendor_id, f"Vendor {vendor_id}"))
                vendors_created.add(vendor_id)
        
        conn.commit()
        
        # Insert real trips
        trips_inserted = 0
        for trip in self.real_trips:
            try:
                cursor = conn.execute("""
                    INSERT INTO Trips (vendor_id, pickup_datetime, dropoff_datetime, 
                                     passenger_count, pickup_longitude, pickup_latitude,
                                     dropoff_longitude, dropoff_latitude, store_and_fwd_flag,
                                     trip_duration_sec)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trip['vendor_id'], trip['pickup_datetime'], trip['dropoff_datetime'],
                    trip['passenger_count'], trip['pickup_longitude'], trip['pickup_latitude'],
                    trip['dropoff_longitude'], trip['dropoff_latitude'], trip['store_and_fwd_flag'],
                    trip['trip_duration_sec']
                ))
                trips_inserted += 1
            except Exception as e:
                print(f"Failed to insert trip: {e}")
        
        conn.commit()
        
        # Verify trips were inserted
        cursor = conn.execute("SELECT COUNT(*) FROM Trips")
        trip_count = cursor.fetchone()[0]
        
        assert trip_count == trips_inserted, f"Expected {trips_inserted} trips, found {trip_count}"
        
        # Test querying trips
        cursor = conn.execute("SELECT * FROM Trips LIMIT 1")
        sample_trip = cursor.fetchone()
        
        assert sample_trip is not None, "Should be able to retrieve a trip"
        assert len(sample_trip) == 11, "Trip should have 11 fields"  # Including trip_id
        
        conn.close()
        print(f"Trip operations test passed - inserted {trips_inserted} real trips")

    def test_real_data_constraints(self):
        """Test that real data meets database constraints"""
        if not self.real_trips:
            print("No real data available, skipping test")
            return
            
        print(f"Testing constraints on {len(self.real_trips)} real trips...")
        
        for i, trip in enumerate(self.real_trips):
            # Test passenger count constraint
            assert trip['passenger_count'] > 0, f"Trip {i}: passenger_count must be positive"
            
            # Test duration constraint
            assert trip['trip_duration_sec'] >= 0, f"Trip {i}: trip_duration_sec must be non-negative"
            
            # Test vendor ID is valid
            assert trip['vendor_id'] > 0, f"Trip {i}: vendor_id must be positive"
            
            # Test coordinates are reasonable for NYC
            assert -75.0 <= trip['pickup_longitude'] <= -73.0, f"Trip {i}: invalid pickup longitude"
            assert 40.0 <= trip['pickup_latitude'] <= 41.0, f"Trip {i}: invalid pickup latitude"
            assert -75.0 <= trip['dropoff_longitude'] <= -73.0, f"Trip {i}: invalid dropoff longitude"
            assert 40.0 <= trip['dropoff_latitude'] <= 41.0, f"Trip {i}: invalid dropoff latitude"
            
        print(f"All {len(self.real_trips)} real trips meet database constraints")

    def test_data_integrity(self):
        """Test referential integrity with real data"""
        if not self.real_trips:
            print("No real data available, skipping test")
            return
            
        # Check that all trips reference valid vendors
        vendor_ids = set()
        for trip in self.real_trips:
            vendor_ids.add(trip['vendor_id'])
        
        assert len(vendor_ids) > 0, "Should have at least one vendor"
        assert all(vid > 0 for vid in vendor_ids), "All vendor IDs should be positive"
        
        # Check data consistency
        for trip in self.real_trips:
            pickup_time = trip['pickup_datetime']
            dropoff_time = trip['dropoff_datetime']
            
            # Basic datetime format check
            assert len(pickup_time) > 10, "Pickup datetime should be reasonable length"
            assert len(dropoff_time) > 10, "Dropoff datetime should be reasonable length"
            
        print(f"Data integrity check passed for {len(vendor_ids)} vendors")


if __name__ == "__main__":
    # Simple test runner
    test = TestDatabase()
    test.setup_method()
    
    try:
        # Run all tests
        test.test_database_connection()
        test.test_vendor_operations()
        test.test_trip_operations_with_real_data()
        test.test_real_data_constraints()
        test.test_data_integrity()
        
        print("All database tests passed!")
        
    finally:
        test.teardown_method()
