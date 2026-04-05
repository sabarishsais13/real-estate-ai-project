from django.urls import path
from .views import RecommendAPIView, RecommendOptionsView, ai_advisor_view

urlpatterns = [
    path('api/recommend/',         RecommendAPIView.as_view(),    name='recommend'),
    path('api/recommend/options/', RecommendOptionsView.as_view(), name='recommend-options'),
    path('ai-advisor/',            ai_advisor_view,                name='ai-advisor'),
]
