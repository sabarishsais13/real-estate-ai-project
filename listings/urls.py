from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('api/properties/',            views.get_properties,       name='get_properties'),
    path('api/properties/<int:pk>/',   views.get_property_detail,  name='get_property_detail'),
    path('api/properties/360/update/', views.update_property_360,  name='update_360'),
    path('api/filter-options/',        views.get_filter_options,   name='filter_options'),

    # UI Pages
    path('',                           views.root_redirect,        name='root'),
    path('home/',                      views.home_page,            name='home'),
    path('discover/',                  views.discover_page,        name='discover'),
    path('property/<int:id>/',         views.property_detail_page, name='property'),
    path('virtual-tour/<int:id>/',     views.virtual_tour_page,    name='virtual_tour'),
    path('sell/',                      views.sell_page,            name='sell'),
    path('ai-advisor/',                views.ai_advisor_page,      name='ai_advisor'),
    path('capture360/',                views.capture360,           name='capture360'),
    path('api/stitch-frames/', views.stitch_frames, name='stitch_frames'),
]