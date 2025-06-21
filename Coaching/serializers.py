from rest_framework import serializers
from .models import CoachingInfo



class CoachingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoachingInfo
        fields = ['name', 'email', 'compyany_name', 'message']
        
    def validate(self, data):
    
        if len(data['message']) < 10:
            raise serializers.ValidationError({
                'message': 'Message must be at least 10 characters long.'
            })
        return data