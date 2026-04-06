from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging

from .ml_model.predict import get_recommendations, VALID_CITIES, VALID_BHK, VALID_TYPES
from .vastu_chatbot import get_answer

logger = logging.getLogger(__name__)


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


@csrf_exempt
def vastu_chat_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        logger.warning("Invalid JSON payload received in vastu chat")
        return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    query = payload.get('query', '').strip()
    if not query:
        logger.warning("Empty query received in vastu chat")
        return JsonResponse({'error': 'Query cannot be blank.'}, status=400)

    logger.debug(f"Vastu Query: '{query}'")
    response_text = get_answer(query)
    logger.debug(f"Vastu Response: '{response_text}'")
    return JsonResponse({'response': response_text})
