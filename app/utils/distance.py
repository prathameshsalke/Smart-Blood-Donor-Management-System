"""
Distance calculation utilities
"""

import math
from geopy.distance import geodesic, great_circle

class DistanceCalculator:
    """Distance calculation utilities"""
    
    EARTH_RADIUS_KM = 6371
    
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        """
        Calculate distance using Haversine formula
        Returns distance in kilometers
        """
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance = DistanceCalculator.EARTH_RADIUS_KM * c
        
        return round(distance, 2)
    
    @staticmethod
    def geodesic(lat1, lon1, lat2, lon2):
        """
        Calculate accurate distance using geodesic method
        Returns distance in kilometers
        """
        try:
            point1 = (lat1, lon1)
            point2 = (lat2, lon2)
            distance = geodesic(point1, point2).kilometers
            return round(distance, 2)
        except:
            # Fallback to haversine
            return DistanceCalculator.haversine(lat1, lon1, lat2, lon2)
    
    @staticmethod
    def great_circle(lat1, lon1, lat2, lon2):
        """
        Calculate distance using great-circle distance
        Returns distance in kilometers
        """
        point1 = (lat1, lon1)
        point2 = (lat2, lon2)
        distance = great_circle(point1, point2).kilometers
        return round(distance, 2)
    
    @staticmethod
    def get_bounding_box(lat, lon, radius_km):
        """
        Get bounding box coordinates for radius search
        Returns (min_lat, max_lat, min_lon, max_lon)
        """
        # Latitude: 1 degree = 111 km
        lat_change = radius_km / 111.0
        
        # Longitude: 1 degree = 111 km * cos(latitude)
        lon_change = radius_km / (111.0 * math.cos(math.radians(lat)))
        
        min_lat = lat - lat_change
        max_lat = lat + lat_change
        min_lon = lon - lon_change
        max_lon = lon + lon_change
        
        return (min_lat, max_lat, min_lon, max_lon)
    
    @staticmethod
    def is_within_radius(lat1, lon1, lat2, lon2, radius_km):
        """Check if point2 is within radius of point1"""
        distance = DistanceCalculator.geodesic(lat1, lon1, lat2, lon2)
        return distance <= radius_km
    
    @staticmethod
    def calculate_bearing(lat1, lon1, lat2, lon2):
        """
        Calculate bearing between two points
        Returns bearing in degrees
        """
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        dlon = lon2 - lon1
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        bearing = math.atan2(x, y)
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360
        
        return round(bearing, 2)
    
    @staticmethod
    def get_direction(bearing):
        """Convert bearing to cardinal direction"""
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        index = round(bearing / 45) % 8
        return directions[index]
    
    @staticmethod
    def calculate_midpoint(lat1, lon1, lat2, lon2):
        """Calculate midpoint between two points"""
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Bx and By
        bx = math.cos(lat2) * math.cos(lon2 - lon1)
        by = math.cos(lat2) * math.sin(lon2 - lon1)
        
        # Midpoint
        lat3 = math.atan2(
            math.sin(lat1) + math.sin(lat2),
            math.sqrt((math.cos(lat1) + bx)**2 + by**2)
        )
        lon3 = lon1 + math.atan2(by, math.cos(lat1) + bx)
        
        # Convert back to degrees
        lat3 = math.degrees(lat3)
        lon3 = math.degrees(lon3)
        
        return (round(lat3, 6), round(lon3, 6))