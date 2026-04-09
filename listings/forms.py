from django import forms
from .models import Property


class PropertyForm(forms.ModelForm):
    CITY_CHOICES = [
        ('', '---------'),
        ('Chennai', 'Chennai'),
        ('Bangalore', 'Bangalore'),
        ('Hyderabad', 'Hyderabad'),
        ('Mumbai', 'Mumbai'),
        ('Coimbatore', 'Coimbatore'),
    ]
    PRICE_CHOICES = [
        ('', '---------'),
        ('15', 'Under ₹ 20 L'),
        ('35', '₹ 20 L - ₹ 50 L'),
        ('75', '₹ 50 L - ₹ 1 Cr'),
        ('150', 'Above ₹ 1 Cr'),
    ]

    city = forms.ChoiceField(choices=CITY_CHOICES, required=True, widget=forms.Select(attrs={'class': 'form-input'}))
    price = forms.ChoiceField(choices=PRICE_CHOICES, required=True, widget=forms.Select(attrs={'class': 'form-input'}))

    class Meta:
        model = Property
        fields = [
            'title', 'location', 'city', 'price', 'bhk', 'type',
            'area', 'floor', 'facing', 'description', 'amenities', 'image'
        ]
        labels = {
            'title': 'Property Title',
            'location': 'Location / Address',
            'city': 'City',
            'price': 'Expected Price',
            'bhk': 'BHK Configuration',
            'type': 'Property Type',
            'area': 'Total Area (sq.ft)',
            'floor': 'Floor Level',
            'facing': 'Property Facing',
            'description': 'Property Description',
            'amenities': 'Featured Amenities',
            'image': 'Upload Image',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Property Title'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Location / Address'}),
            # city and price widgets are now defined directly on their ChoiceField overrides.
            'bhk': forms.Select(attrs={'class': 'form-input'}),
            'type': forms.Select(attrs={'class': 'form-input'}),
            'area': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Area (sq.ft)'}),
            'floor': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Floor'}),
            'facing': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Facing'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Description'}),
            'amenities': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Amenities'}),
            'image': forms.FileInput(attrs={'class': 'file-input', 'accept': 'image/png,image/jpeg,image/jpg'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make image required for new properties
        if not self.instance.pk:
            self.fields['image'].required = True

    def clean_price(self):
        price_value = self.cleaned_data.get('price')
        price_options = {
            '15': 'Under ₹ 20 L',
            '35': '₹ 20 L - ₹ 50 L',
            '75': '₹ 50 L - ₹ 1 Cr',
            '150': 'Above ₹ 1 Cr',
        }
        return price_options.get(price_value, price_value)