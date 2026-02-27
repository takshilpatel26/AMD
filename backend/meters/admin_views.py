"""
Admin Views - Village Data API for Government/Admin Panel
Provides real-time village grid monitoring data
"""

import csv
import random
from datetime import datetime
from pathlib import Path
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User


class AdminLoginView(APIView):
    """
    Admin login endpoint with simple username/password authentication
    POST /api/v1/admin/login/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Username and password required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Try to authenticate
        user = None
        
        # First check if user exists by username
        try:
            user_obj = User.objects.get(username=username)
            if user_obj.check_password(password):
                user = user_obj
        except User.DoesNotExist:
            pass
        
        # Also check by phone number for backward compatibility
        if not user:
            try:
                user_obj = User.objects.get(phone_number=username)
                if user_obj.check_password(password):
                    user = user_obj
            except User.DoesNotExist:
                pass
        
        if not user:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user is admin (utility or government role)
        if user.role not in ['utility', 'government', 'admin']:
            return Response(
                {'error': 'Admin access required. You do not have admin privileges.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Admin login successful',
            'user': {
                'id': str(user.id),
                'username': user.username,
                'name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'role': user.role,
                'phone_number': user.phone_number,
            },
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        })


class VillageDataView(APIView):
    """
    Village Grid Data API for Admin Panel
    GET /api/v1/admin/villagedata/
    
    Returns real-time village grid monitoring data with voltage, 
    power usage, and status for all houses.
    """
    permission_classes = [AllowAny]  # For demo - change to IsAuthenticated for production
    
    def get(self, request):
        # Check for admin role if authenticated
        if request.user and request.user.is_authenticated:
            if request.user.role not in ['utility', 'government', 'admin']:
                return Response(
                    {'error': 'Admin access required'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Load village data from CSV or generate dynamic data
        village_data = self._generate_village_data()
        
        # Calculate summary statistics
        total_houses = len(village_data)
        normal_count = sum(1 for h in village_data if 'Normal' in h['status_note'] or 'Optimal' in h['status_note'])
        brownout_count = sum(1 for h in village_data if 'Brownout' in h['status_note'] or 'Low' in h['status_note'])
        high_voltage_count = sum(1 for h in village_data if 'High' in h['status_note'])
        surge_count = sum(1 for h in village_data if 'Surge' in h['status_note'] or 'Overvoltage' in h['status_note'])
        outage_count = sum(1 for h in village_data if 'Outage' in h['status_note'])
        critical_count = sum(1 for h in village_data if 'Critical' in h['status_note'])
        
        avg_voltage = sum(h['voltage'] for h in village_data) / total_houses if total_houses > 0 else 0
        total_power = sum(h['usage_kw'] for h in village_data)
        
        return Response({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_houses': total_houses,
                'normal': normal_count,
                'brownout': brownout_count,
                'high_voltage': high_voltage_count,
                'surge': surge_count,
                'outage': outage_count,
                'critical': critical_count,
                'avg_voltage': round(avg_voltage, 2),
                'total_power_kw': round(total_power, 2),
            },
            'houses': village_data
        })
    
    def _get_status_note(self, voltage, usage_kw):
        """Rule-based engine to determine status based on voltage and usage"""
        if voltage == 0:
            return "🚨 Power Outage"
        elif voltage > 280:
            return "⚡ Severe Overvoltage"
        elif voltage > 250:
            return "⚠️ High Voltage Surge"
        elif voltage < 180:
            return "🛑 Brownout Level"
        elif voltage < 200:
            return "📉 Low Supply"
        elif usage_kw > 12:
            return "🔥 Critical Load"
        elif usage_kw > 10:
            return "⚡ High Load"
        else:
            return "✅ Normal"
    
    def _generate_village_data(self):
        """Generate dynamic village data for 500 houses"""
        # Try to load base data from CSV
        csv_path = Path(__file__).parent.parent.parent / 'Admin console' / 'dataforgovpanel.csv'
        
        base_names = [
            "Aarush Mukherjee", "Harshil Shrivastav", "Meera Jain", "Simran Mukherjee",
            "Ishaan Shrivastav", "Nisha Singh", "Maya Rao", "Varun Sharma",
            "Sanjana Agarwal", "Lekha Tripathi", "Harshil Verma", "Avni Dwivedi",
            "Prateek Naidu", "Karan Bansal", "Devansh Deshmukh", "Ishani Menon",
            "Jatin Deshmukh", "Tanisha Seth", "Ananya Seth", "Aarush Deshpande",
            "Rishabh Dwivedi", "Vikram Shrivastav", "Anya Iyer", "Navya Chauhan",
            "Maya Reddy", "Harshil Patel", "Sameer Kunj", "Sneha Nair",
            "Divya Srinivasan", "Arjun Rathore", "Kunal Jha", "Dhruv Chaudhary",
        ]
        
        village_data = []
        
        for i in range(500):
            # Generate house ID
            house_id = f"HOUSE-{i+1:04d}"
            
            # Select name
            name = base_names[i % len(base_names)]
            
            # Generate realistic voltage with realistic distribution
            chance = random.random()
            if chance < 0.001:  # 0.1% outage
                voltage = 0.0
                usage_kw = 0.0
            elif chance < 0.003:  # 0.2% surge
                voltage = round(random.uniform(260.0, 290.0), 1)
                usage_kw = round(random.uniform(0.5, 2.0), 2)
            elif chance < 0.05:  # 5% brownout
                voltage = round(random.uniform(175.0, 195.0), 1)
                usage_kw = round(random.uniform(0.5, 8.0), 2)
            elif chance < 0.10:  # 5% high voltage
                voltage = round(random.uniform(245.0, 260.0), 1)
                usage_kw = round(random.uniform(0.5, 8.0), 2)
            else:  # ~90% normal
                voltage = round(230.0 + random.uniform(-15.0, 15.0), 1)
                usage_kw = round(random.uniform(0.5, 10.0), 2)
            
            # Determine status
            status_note = self._get_status_note(voltage, usage_kw)
            
            village_data.append({
                'house_id': house_id,
                'name': name,
                'voltage': voltage,
                'usage_kw': usage_kw,
                'status_note': status_note,
                'last_updated': datetime.now().strftime("%H:%M:%S"),
            })
        
        return village_data


class VillageDataStreamView(APIView):
    """
    Streaming endpoint for real-time updates (for polling)
    GET /api/v1/admin/villagedata/stream/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Get updated data
        village_view = VillageDataView()
        village_data = village_view._generate_village_data()
        
        return Response({
            'timestamp': datetime.now().isoformat(),
            'house_count': len(village_data),
            'houses': village_data
        })
