from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from users.api.serializers import UserSerializer,DivisionalOfficeSignUpSerializer,SubDivisionalOfficeSignUpSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from users.api.permissions import IsDivisionalOffice,IsSubDivisionalOffice

class DivisionalOfficeSignUpView(generics.GenericAPIView):
    serializer_class=DivisionalOfficeSignUpSerializer

    def post(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.save()
        return Response({
            "user":UserSerializer(user,context=self.get_serializer_context).data,
            "token":Token.objects.get(user=user).key,
            "message":"Account created Succesfully"
        }
        )

class SubDivisionalOfficeSignUpView(generics.GenericAPIView):
    serializer_class=SubDivisionalOfficeSignUpSerializer

    def post(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.save()
        return Response({
            "user":UserSerializer(user,context=self.get_serializer_context).data,
            "token":Token.objects.get(user=user).key,
            "message":"Account created Succesfully"
        }
        )

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer=self.serializer_class(data=request.data,context={'request':request})
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']

        token,created = Token.objects.get_or_create(user=user)

        return Response({
            'token':token.key,
            'user_id':user.pk,
            'is_divisional':user.is_divisional,
            'is_sub_divisional':user.is_sub_divisional
        })
    

class LogoutView(APIView):
    def post(self, request, format=None):
        request.auth.delete()
        return Response(status=HTTP_200_OK)

class DivisionOnlyView(generics.RetrieveAPIView):
    permission_classes=[permissions.IsAuthenticated& IsDivisionalOffice]
    serializer_class=UserSerializer

    def get_object(self):
        return self.request.user
    
class SubDivisionOnlyView(generics.RetrieveAPIView):
    permission_classes=[permissions.IsAuthenticated& IsSubDivisionalOffice]
    serializer_class=UserSerializer

    def get_object(self):
        return self.request.user
