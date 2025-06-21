from rest_framework import serializers
from .models import ContactMessage

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        
    def validate(self, data):
        if len(data['message']) < 10:
            raise serializers.ValidationError({
                'message': 'Message must be at least 10 characters long.'
            })
        return data