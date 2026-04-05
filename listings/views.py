from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Property
from .serializers import PropertySerializer

# ── UI Pages ──────────────────────────────────────────────

def root_redirect(request):
    return redirect('home')

def home_page(request):
    return render(request, 'home.html')

def discover_page(request):
    return render(request, 'discover.html')

def property_detail_page(request, id):
    # Just render the template. The frontend will fetch data via API or we can pass it here.
    # We will pass the property ID so JS can fetch or we can pass context.
    return render(request, 'property_detail.html', {'property_id': id})

def virtual_tour_page(request, id):
    return render(request, 'virtual_tour.html', {'property_id': id})

def sell_page(request):
    if request.method == 'POST':
        price_value_str = request.POST.get('price')
        price_options = {
            '15': '₹ 15 L',
            '35': '₹ 35 L',
            '75': '₹ 75 L',
            '150': '₹ 150 L',
        }
        price = price_options.get(price_value_str, price_value_str)

        new_property = Property.objects.create(
            title=request.POST.get('title'),
            location=request.POST.get('location'),
            price=price,
            price_value=float(price_value_str),
            bhk=request.POST.get('bhk'),
            type=request.POST.get('type'),
            area=request.POST.get('area'),
            floor=request.POST.get('floor'),
            facing=request.POST.get('facing'),
            description=request.POST.get('description'),
            amenities=request.POST.get('amenities'),
            image=request.FILES.get('image'),  # File upload
            city=request.POST.get('city'),
            is_active=True
        )

        # Redirect to capture360 with the new property ID
        return redirect(f'/capture360/?property_id={new_property.id}')

    return render(request, 'sell.html')

def ai_advisor_page(request):
    return render(request, 'ai_advisor.html')

def capture360(request):
    return render(request, 'capture360.html')


# ── GET all properties with filters ─────────────────────────────
@api_view(['GET'])
def get_properties(request):
    queryset = Property.objects.filter(is_active=True)

    city      = request.GET.get('city',   None)
    budget    = request.GET.get('budget', None)
    prop_type = request.GET.get('type',   None)
    bhk       = request.GET.get('bhk',    None)

    if city and city != 'all' and city != 'All':
        # Assuming city might be stored in location or city field.
        # Using icontains on location for flexibility.
        from django.db.models import Q
        queryset = queryset.filter(Q(city__iexact=city) | Q(location__icontains=city))

    if prop_type and prop_type != 'all':
        queryset = queryset.filter(type=prop_type)

    if bhk and bhk != 'all':
        queryset = queryset.filter(bhk=bhk)

    # Budget filter in Lakhs
    if budget and budget != 'all':
        if budget == 'under20':
            queryset = queryset.filter(price_value__lt=20)
        elif budget == '20to50':
            queryset = queryset.filter(price_value__gte=20,  price_value__lt=50)
        elif budget == '50to100':
            queryset = queryset.filter(price_value__gte=50,  price_value__lt=100)
        elif budget == 'above100':
            queryset = queryset.filter(price_value__gte=100)

    serializer = PropertySerializer(queryset, many=True, context={'request': request})
    return Response({
        'count':      queryset.count(),
        'properties': serializer.data
    }, status=status.HTTP_200_OK)


# ── GET single property by ID ────────────────────────────────────
@api_view(['GET'])
def get_property_detail(request, pk):
    try:
        prop = Property.objects.get(pk=pk, is_active=True)
    except Property.DoesNotExist:
        return Response(
            {'error': 'Property not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = PropertySerializer(prop, context={'request': request})
    return Response(serializer.data)


# ── UPDATE property 360 views ───────────────────────────────────────
@api_view(['POST'])
def update_property_360(request):
    """Save 360-degree views for a property"""
    try:
        property_id = request.data.get('property_id')
        if not property_id:
            return Response(
                {'error': 'property_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        prop = Property.objects.get(pk=property_id, is_active=True)

        # Update 360 view fields
        if request.data.get('living_room_360'):
            prop.living_room_360 = request.data.get('living_room_360')
        if request.data.get('kitchen_360'):
            prop.kitchen_360 = request.data.get('kitchen_360')
        if request.data.get('bedroom_360'):
            prop.bedroom_360 = request.data.get('bedroom_360')
        if request.data.get('bathroom_360'):
            prop.bathroom_360 = request.data.get('bathroom_360')

        prop.save()

        return Response(
            {'status': 'success', 'message': '360 views updated'},
            status=status.HTTP_200_OK
        )
    except Property.DoesNotExist:
        return Response(
            {'error': 'Property not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


# ── GET filter dropdown options ──────────────────────────────────
@api_view(['GET'])
def get_filter_options(request):
    # Static options as defined in the plan/UI
    cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad']
    types = ['Apartment', 'Villa', 'Independent House', 'Plot', 'Studio', 'Penthouse']
    bhks = ['Studio', '1 BHK', '2 BHK', '3 BHK', '4 BHK', '5 BHK', 'Plot']
    
    return Response({
        'cities':  cities,
        'types':   types,
        'bhk':     bhks,
        'budgets': [
            {'value': 'under20',  'label': 'Under \u20b920L'},
            {'value': '20to50',   'label': '\u20b920L \u2013 \u20b950L'},
            {'value': '50to100',  'label': '\u20b950L \u2013 \u20b91Cr'},
            {'value': 'above100', 'label': 'Above \u20b91Cr'},
        ]
    })
