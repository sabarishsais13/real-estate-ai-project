from rest_framework import serializers
from .models import Property

class PropertySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = '__all__'

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            image_url = obj.image.url
            if request:
                return request.build_absolute_uri(image_url)
            return image_url
        return 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800'
