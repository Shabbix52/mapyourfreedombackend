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

class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()  # Always show all books

    def get_serializer_context(self):
        user = self.request.user
        if user and user.is_authenticated:
            return {
                'user_books': set(user.books.values_list('id', flat=True)),
            }
        return {}

    @action(['GET'], detail=True)
    def get_book(self, request, pk=None):
        print(f"get_book called for user: {request.user} (id={request.user.id}) and book id: {pk}")
        try:
            book = Book.objects.get(id=pk)
            print(f"Book found: {book} (id={book.id}, language={book.language}, path={book.path})")
        except Book.DoesNotExist:
            print("Book not found!")
            return Response({'detail': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)

        # Only allow if user has access
        user_books = list(request.user.books.values_list('id', flat=True))
        print(f"User's accessible books: {user_books}")
        if not request.user.is_superuser and book.id not in user_books:
            print("Access forbidden: user does not have this book.")
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        if not book.path:
            print("Book file path is empty!")
            return Response({'detail': 'No file'}, status=status.HTTP_404_NOT_FOUND)

        file_path = book.path.path
        print(f"Book file path on disk: {file_path}")
        if not os.path.exists(file_path):
            print("Book file does not exist on disk!")
            return Response({'detail': 'File missing on server'}, status=status.HTTP_404_NOT_FOUND)

        try:
            file = book.path.open('rb')
            response = HttpResponse(content=file, status=status.HTTP_200_OK, content_type='application/pdf')
            response['Content-Disposition'] = f"inline; filename={book.name}"
            response['Content-Length'] = os.path.getsize(file_path)
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['X-Frame-Options'] = 'DENY'
            response['Content-Security-Policy'] = "default-src 'none'; frame-ancestors 'none'"
            print("PDF served successfully.")
            return response
        except Exception as error:
            print(f"Error serving PDF: {error}")
            return Response({"detail": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
