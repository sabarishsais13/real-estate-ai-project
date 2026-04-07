from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F
from .models import Property, PropertyInteraction
from .serializers import PropertySerializer
import cv2
import numpy as np
import base64
import json
from django.http import JsonResponse
from django.core.exceptions import RequestDataTooBig

# ── UI Pages ──────────────────────────────────────────────

def root_redirect(request):
    return redirect('home')

def home_page(request):
    return render(request, 'home.html')

def discover_page(request):
    return render(request, 'discover.html')

def property_detail_page(request, id):
    return render(request, 'property_detail.html', {'property_id': id})

def virtual_tour_page(request, id):
    return render(request, 'virtual_tour.html', {'property_id': id})

@login_required
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
            image=request.FILES.get('image'),
            city=request.POST.get('city'),
            is_active=True,
            owner=request.user,
        )
        PropertyInteraction.objects.create(
            user=request.user,
            property=new_property,
            interaction_type=PropertyInteraction.SUBMIT,
        )

        return redirect(f'/capture360/?property_id={new_property.id}')

    return render(request, 'sell.html')

def ai_advisor_page(request):
    return render(request, 'ai_advisor.html')

@login_required
def capture360(request):
    property_id = request.GET.get('property_id')
    return render(request, 'capture360.html', {'property_id': property_id})


@login_required
def edit_property_page(request, id):
    prop = get_object_or_404(Property, id=id, owner=request.user)

    if request.method == "POST":
        price_value_str = request.POST.get('price')
        price_options = {
            '15': '₹ 15 L',
            '35': '₹ 35 L',
            '75': '₹ 75 L',
            '150': '₹ 150 L',
        }
        prop.title = request.POST.get('title')
        prop.location = request.POST.get('location')
        prop.city = request.POST.get('city')
        if price_value_str:
            prop.price_value = float(price_value_str)
            prop.price = price_options.get(price_value_str, price_value_str)
        prop.bhk = request.POST.get('bhk')
        prop.type = request.POST.get('type')
        prop.area = request.POST.get('area')
        prop.floor = request.POST.get('floor')
        prop.facing = request.POST.get('facing')
        prop.description = request.POST.get('description')
        prop.amenities = request.POST.get('amenities')

        if request.FILES.get('image'):
            prop.image = request.FILES.get('image')

        prop.save()
        messages.success(request, "Property updated successfully.")
        return redirect("dashboard")

    return render(request, "edit_property.html", {"property": prop})

def stitch_frames(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except RequestDataTooBig:
            return JsonResponse(
                {'error': 'Captured frames are too large. Please capture again with fewer/shorter frames.'},
                status=413
            )
        except Exception:
            return JsonResponse({'error': 'Invalid stitch payload'}, status=400)
        frames_b64 = data.get('frames', [])

        images = []
        for f in frames_b64:
            img_data = base64.b64decode(f.split(',')[1])
            np_arr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if img is not None:
                images.append(img)

        if len(images) < 2:
            return JsonResponse({'error': 'Need at least 2 frames'}, status=400)

        stitcher = cv2.Stitcher.create(cv2.Stitcher_PANORAMA)
        stitch_status, stitched = stitcher.stitch(images)

        if stitch_status == cv2.Stitcher_OK:
            _, buffer = cv2.imencode('.jpg', stitched)
            stitched_b64 = base64.b64encode(buffer).decode('utf-8')
            return JsonResponse({'image': f'data:image/jpeg;base64,{stitched_b64}'})
        else:
            return JsonResponse({'error': 'Stitching failed'}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


# ── GET all properties with filters ─────────────────────────────
@api_view(['GET'])
def get_properties(request):
    queryset = Property.objects.filter(is_active=True)

    city      = request.GET.get('city',   None)
    budget    = request.GET.get('budget', None)
    prop_type = request.GET.get('type',   None)
    bhk       = request.GET.get('bhk',    None)

    if city and city != 'all' and city != 'All':
        from django.db.models import Q
        queryset = queryset.filter(Q(city__iexact=city) | Q(location__icontains=city))

    if prop_type and prop_type != 'all':
        queryset = queryset.filter(type=prop_type)

    if bhk and bhk != 'all':
        queryset = queryset.filter(bhk=bhk)

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
    Property.objects.filter(pk=prop.pk).update(views_count=F("views_count") + 1)
    prop.refresh_from_db()
    if request.user.is_authenticated:
        PropertyInteraction.objects.create(
            user=request.user,
            property=prop,
            interaction_type=PropertyInteraction.VIEW,
        )
    serializer = PropertySerializer(prop, context={'request': request})
    return Response(serializer.data)


# ── UPDATE property 360 views ───────────────────────────────────────
@api_view(['POST'])
def update_property_360(request):
    try:
        property_id = request.data.get('property_id')
        if not property_id:
            return Response(
                {'error': 'property_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        prop = Property.objects.get(pk=property_id, is_active=True)
        if request.user.is_authenticated and prop.owner_id and prop.owner_id != request.user.id:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

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


@api_view(['POST'])
def track_property_interaction(request):
    property_id = request.data.get("property_id")
    interaction_type = request.data.get("interaction_type", PropertyInteraction.CLICK)

    if not request.user.is_authenticated:
        return Response({"status": "ignored"}, status=status.HTTP_200_OK)

    if interaction_type not in dict(PropertyInteraction.INTERACTION_CHOICES):
        return Response({"error": "Invalid interaction_type"}, status=status.HTTP_400_BAD_REQUEST)

    prop = get_object_or_404(Property, pk=property_id, is_active=True)
    PropertyInteraction.objects.create(
        user=request.user,
        property=prop,
        interaction_type=interaction_type,
    )
    return Response({"status": "tracked"}, status=status.HTTP_201_CREATED)


# ── GET filter dropdown options ──────────────────────────────────
@api_view(['GET'])
def get_filter_options(request):
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