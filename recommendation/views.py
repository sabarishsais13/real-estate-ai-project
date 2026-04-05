from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
import os, sys

# Add ml_model path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ml_model'))
from predict import get_recommendations, VALID_CITIES, VALID_BHK, VALID_TYPES


class RecommendAPIView(APIView):
    """
    POST /api/recommend/
    Body: { "city": "Mumbai", "bhk": "2 BHK", "type": "Apartment", "budget": 80 }
    """
    def post(self, request):
        city      = request.data.get('city', '')
        bhk       = request.data.get('bhk', '')
        prop_type = request.data.get('type', '')
        budget    = float(request.data.get('budget', 50))

        if not city or not bhk or not prop_type:
            return Response(
                {'error': 'city, bhk, and type are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        results = get_recommendations(city, bhk, prop_type, budget, top_n=3)

        return Response({
            'status':  'success',
            'count':   len(results),
            'results': results
        })


class RecommendOptionsView(APIView):
    """
    GET /api/recommend/options/
    Returns valid dropdown values for the frontend form
    """
    def get(self, request):
        return Response({
            'cities': VALID_CITIES,
            'bhk':    VALID_BHK,
            'types':  VALID_TYPES,
        })


def ai_advisor_view(request):
    """Renders ai_advisor.html page"""
    return render(request, 'ai_advisor.html', {
        'cities': VALID_CITIES,
        'bhk':    VALID_BHK,
        'types':  VALID_TYPES,
    })
