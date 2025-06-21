import os
from django.contrib.auth import get_user_model
from django.http import StreamingHttpResponse, HttpResponse
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from djoser.views import UserViewSet
from djoser.compat import get_user_email
from djoser.conf import settings as djoser_settings

from .models import Book
from .serializers import BookSerializer, CustomPasswordResetConfirmRetypeSerializer

# Create your views here.

user = get_user_model()

class CustomUserViewSet(UserViewSet):
    
    @action(["post"], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = CustomPasswordResetConfirmRetypeSerializer(
                        data=request.data, 
                        context={
                            'view': self,
                            'request': request
                        }
                    )
        serializer.is_valid(raise_exception=True)
        if djoser_settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {'user': serializer.save()}
            to = [get_user_email(serializer.instance)]
            djoser_settings.EMAIL.password_changed_confirmation(self.request, context).send(to)
        return Response(status=status.HTTP_204_NO_CONTENT)

class BookViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_serializer_context(self):
        user = self.request.user
        if user:
            return {
                'has_ev_access': user.has_ev_access, 
                'has_sv_access': user.has_sv_access, 
            }
        
        return {}

    @action(['GET'], detail=True)
    def get_book(self, request, pk=None):
        
        permission_mapping = {
            'english': 'has_ev_access',
            'spanish': 'has_sv_access' 
        }

        book = Book.objects.get(id = self.kwargs['pk'])
        if not book:
            return Response({
                'detail': 'Not Found' 
            }, status=status.HTTP_404_NOT_FOUND)
        
        
        if not getattr(request.user, permission_mapping[book.language]):
            return Response({
                "detail": "Forbidden"
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            file = book.path.open('rb')

            response = HttpResponse(content=file, status=status.HTTP_200_OK, content_type='application/pdf')
            response['Content-Disposition'] = f"inline; filename={book.name}"
            response['Content-Length'] = os.path.getsize(book.path.path)
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['X-Frame-Options'] = 'DENY'
            response['Content-Security-Policy'] = "default-src 'none'; frame-ancestors 'none'"
            
            return response
        
        except Exception as error:
            print(error)

            return Response({
                "detail": "Internal Server Error" 
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
