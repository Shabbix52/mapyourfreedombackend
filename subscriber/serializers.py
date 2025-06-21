# from rest_framework import serializers
# from .models import Subscriber

# class SubscriberSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Subscriber
#         fields = ['first_name', 'last_name', 'email']
        
#     def validate_email(self, value):
#         # Check if this email already exists and is active
#         if Subscriber.objects.filter(email=value, is_active=True).exists():
#             raise serializers.ValidationError("This email is already subscribed to our newsletter.")
#         return value
    
#     def validate(self, data):
#         # Add additional validation if needed
#         if len(data['first_name']) < 2:
#             raise serializers.ValidationError({
#                 'first_name': 'First name must be at least 2 characters long.'
#             })
#         if len(data['last_name']) < 2:
#             raise serializers.ValidationError({
#                 'last_name': 'Last name must be at least 2 characters long.'
#             })
#         return data



from rest_framework import serializers
from .models import Subscriber

class SubscriberSerializer(serializers.ModelSerializer):
    notify_admin = serializers.BooleanField(default=False, required=False)
    
    class Meta:
        model = Subscriber
        fields = ['first_name', 'last_name', 'email', 'notify_admin']
        
    def validate_email(self, value):
        """
        Check if email already exists and is active
        """
        if Subscriber.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("This email is already subscribed to our newsletter.")
        return value