from django import forms
from .models import Property


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'location', 'city', 'price', 'bhk', 'type',
            'area', 'floor', 'facing', 'description', 'amenities', 'image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Property Title'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Location / Address'}),
            'city': forms.Select(attrs={'class': 'form-input'}),
            'price': forms.Select(attrs={'class': 'form-input'}),
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
            '15': '₹ 15 L',
            '35': '₹ 35 L',
            '75': '₹ 75 L',
            '150': '₹ 150 L',
        }
        return price_options.get(price_value, price_value)