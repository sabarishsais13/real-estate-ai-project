from django.core.management.base import BaseCommand
from listings.models import Property

class Command(BaseCommand):
    help = 'Seed database with 12 general real estate properties'

    def handle(self, *args, **kwargs):
        Property.objects.all().delete()

        properties = [
            {
                "title": "Sunrise Apartments",
                "location": "Andheri, Mumbai",       "city": "Mumbai",
                "price": "\u20b9 45 L",              "price_value": 45,
                "bhk": "1 BHK",                      "area": "550 sq.ft",
                "floor": "3",                         "type": "Apartment",
                "badge": "AFFORDABLE",
                "image": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800"
            },
            {
                "title": "Green Valley Homes",
                "location": "Whitefield, Bangalore",  "city": "Bangalore",
                "price": "\u20b9 62 L",              "price_value": 62,
                "bhk": "2 BHK",                      "area": "980 sq.ft",
                "floor": "2",                         "type": "Apartment",
                "badge": "NEW",
                "image": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800"
            },
            {
                "title": "Shanti Nagar Residency",
                "location": "Dwarka, Delhi",          "city": "Delhi",
                "price": "\u20b9 78 L",              "price_value": 78,
                "bhk": "3 BHK",                      "area": "1250 sq.ft",
                "floor": "5",                         "type": "Apartment",
                "badge": "TRENDING",
                "image": "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800"
            },
            {
                "title": "Chennai Central Flats",
                "location": "Tambaram, Chennai",      "city": "Chennai",
                "price": "\u20b9 38 L",              "price_value": 38,
                "bhk": "2 BHK",                      "area": "820 sq.ft",
                "floor": "1",                         "type": "Apartment",
                "badge": "",
                "image": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800"
            },
            {
                "title": "Tulip Garden Villas",
                "location": "Gachibowli, Hyderabad",  "city": "Hyderabad",
                "price": "\u20b9 95 L",              "price_value": 95,
                "bhk": "3 BHK",                      "area": "1600 sq.ft",
                "floor": "G",                         "type": "Villa",
                "badge": "POPULAR",
                "image": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=800"
            },
            {
                "title": "Metro View Apartments",
                "location": "Bandra, Mumbai",         "city": "Mumbai",
                "price": "\u20b9 1.1 Cr",            "price_value": 110,
                "bhk": "2 BHK",                      "area": "1050 sq.ft",
                "floor": "8",                         "type": "Apartment",
                "badge": "NEW",
                "image": "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800"
            },
            {
                "title": "Prakruthi Independent House",
                "location": "Sarjapur, Bangalore",    "city": "Bangalore",
                "price": "\u20b9 88 L",              "price_value": 88,
                "bhk": "3 BHK",                      "area": "1800 sq.ft",
                "floor": "G+1",                       "type": "Independent House",
                "badge": "",
                "image": "https://images.unsplash.com/photo-1572120360610-d971b9d7767c?w=800"
            },
            {
                "title": "Budget Studio Suites",
                "location": "Kondapur, Hyderabad",    "city": "Hyderabad",
                "price": "\u20b9 18 L",              "price_value": 18,
                "bhk": "Studio",                     "area": "320 sq.ft",
                "floor": "4",                         "type": "Apartment",
                "badge": "AFFORDABLE",
                "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"
            },
            {
                "title": "Capital Heights",
                "location": "Rohini, Delhi",          "city": "Delhi",
                "price": "\u20b9 55 L",              "price_value": 55,
                "bhk": "2 BHK",                      "area": "900 sq.ft",
                "floor": "6",                         "type": "Apartment",
                "badge": "TRENDING",
                "image": "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800"
            },
            {
                "title": "Kaveri River Plots",
                "location": "Perambur, Chennai",      "city": "Chennai",
                "price": "\u20b9 22 L",              "price_value": 22,
                "bhk": "Plot",                       "area": "1200 sq.ft",
                "floor": "G",                         "type": "Plot",
                "badge": "",
                "image": "https://images.unsplash.com/photo-1600210492493-0946911123ea?w=800"
            },
            {
                "title": "Horizon Family Homes",
                "location": "Thane, Mumbai",          "city": "Mumbai",
                "price": "\u20b9 72 L",              "price_value": 72,
                "bhk": "3 BHK",                      "area": "1350 sq.ft",
                "floor": "7",                         "type": "Apartment",
                "badge": "POPULAR",
                "image": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800"
            },
            {
                "title": "Electronic City Nest",
                "location": "Electronic City, Bangalore", "city": "Bangalore",
                "price": "\u20b9 48 L",              "price_value": 48,
                "bhk": "2 BHK",                      "area": "875 sq.ft",
                "floor": "3",                         "type": "Apartment",
                "badge": "NEW",
                "image": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800"
            },
        ]

        for p in properties:
            Property.objects.create(**p)

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded {len(properties)} properties!'
        ))
