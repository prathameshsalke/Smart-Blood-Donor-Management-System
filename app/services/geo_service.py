"""
Geo Service for location-based operations
"""

import math
import requests
from geopy.distance import geodesic
from app.repositories.donor_repo import DonorRepository
from app.repositories.hospital_repo import HospitalRepository
from flask import current_app

class GeoService:
    """Service for handling geo-location operations"""
    
    EARTH_RADIUS_KM = 6371
    
    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """
        Calculate distance between two points using Haversine formula
        Returns distance in kilometers
        """
        try:
            # Convert decimal degrees to radians
            lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
            
            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            distance = GeoService.EARTH_RADIUS_KM * c
            
            return round(distance, 2)
        except (ValueError, TypeError) as e:
            current_app.logger.error(f"Error calculating haversine distance: {e}")
            return float('inf')
    
    @staticmethod
    def geodesic_distance(lat1, lon1, lat2, lon2):
        """
        Calculate more accurate distance using geodesic method
        """
        try:
            point1 = (float(lat1), float(lon1))
            point2 = (float(lat2), float(lon2))
            distance = geodesic(point1, point2).kilometers
            return round(distance, 2)
        except Exception as e:
            current_app.logger.error(f"Geodesic distance error: {e}")
            return GeoService.haversine_distance(lat1, lon1, lat2, lon2)
    
    @staticmethod
    def find_nearby_donors(latitude, longitude, radius_km=10, blood_type=None, include_all=False):
        """
        Find donors within specified radius
        If include_all is True, returns all donors with distance info
        """
        try:
            # Validate inputs
            if latitude is None or longitude is None:
                current_app.logger.error("Latitude or longitude is None")
                return []
            
            latitude = float(latitude)
            longitude = float(longitude)
            radius_km = float(radius_km)
            
            # Get all eligible donors
            donors = DonorRepository.get_eligible_donors()
            nearby_donors = []
            all_donors_with_distance = []
            
            for donor in donors:
                # Skip donors without location
                if donor.latitude is None or donor.longitude is None:
                    continue
                
                try:
                    # Calculate distance
                    distance = GeoService.geodesic_distance(
                        latitude, longitude,
                        donor.latitude, donor.longitude
                    )
                    
                    donor_dict = donor.to_dict()
                    donor_dict['distance_km'] = distance
                    
                    # Add to all donors list
                    all_donors_with_distance.append(donor_dict)
                    
                    # Check if within radius
                    if distance <= radius_km:
                        # Filter by blood type if specified
                        if blood_type and donor.blood_type != blood_type:
                            continue
                        
                        nearby_donors.append(donor_dict)
                        
                except Exception as e:
                    current_app.logger.error(f"Error processing donor {donor.id}: {e}")
                    continue
            
            # Sort all donors by distance
            all_donors_with_distance.sort(key=lambda x: x['distance_km'])
            
            # If include_all is True, return all donors sorted by distance
            if include_all:
                return all_donors_with_distance
            
            # Otherwise return only nearby donors
            nearby_donors.sort(key=lambda x: x['distance_km'])
            return nearby_donors
            
        except Exception as e:
            current_app.logger.error(f"Error finding nearby donors: {e}")
            return []
    
    @staticmethod
    def find_nearby_hospitals(latitude, longitude, radius_km=20):
        """
        Find hospitals within specified radius
        """
        try:
            # Validate inputs
            if latitude is None or longitude is None:
                current_app.logger.error("Latitude or longitude is None")
                return []
            
            latitude = float(latitude)
            longitude = float(longitude)
            radius_km = float(radius_km)
            
            hospitals = HospitalRepository.get_all_verified()
            nearby_hospitals = []
            
            for hospital in hospitals:
                try:
                    distance = GeoService.geodesic_distance(
                        latitude, longitude,
                        hospital.latitude, hospital.longitude
                    )
                    
                    hospital_dict = hospital.to_dict()
                    hospital_dict['distance_km'] = distance
                    
                    if distance <= radius_km:
                        nearby_hospitals.append(hospital_dict)
                except Exception as e:
                    current_app.logger.error(f"Error processing hospital {hospital.id}: {e}")
                    continue
            
            # Sort by distance
            nearby_hospitals.sort(key=lambda x: x['distance_km'])
            
            return nearby_hospitals
            
        except Exception as e:
            current_app.logger.error(f"Error finding nearby hospitals: {e}")
            return []
    
    @staticmethod
    def reverse_geocode(latitude, longitude):
        """
        Get address information from coordinates using OpenStreetMap Nominatim
        """
        try:
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': latitude,
                'lon': longitude,
                'format': 'json',
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'BloodDonorFinder/1.0'  # Required by Nominatim
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                address = data.get('address', {})
                
                # Extract address components
                result = {
                    'address': data.get('display_name', ''),
                    'city': address.get('city') or address.get('town') or address.get('village') or address.get('suburb', ''),
                    'state': address.get('state', ''),
                    'country': address.get('country', ''),
                    'pincode': address.get('postcode', ''),
                    'road': address.get('road', ''),
                    'suburb': address.get('suburb', '')
                }
                return result
            else:
                current_app.logger.error(f"Reverse geocoding failed: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            current_app.logger.error("Reverse geocoding timeout")
            return None
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Reverse geocoding error: {e}")
            return None
        except Exception as e:
            current_app.logger.error(f"Unexpected reverse geocoding error: {e}")
            return None