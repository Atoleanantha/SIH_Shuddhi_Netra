from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from users.models import DivisionalOffice,SubDivisionalOffice
from users.api.serializers import UserSerializer,DivisionalOfficeSignUpSerializer,SubDivisionalOfficeSignUpSerializer,DivisionalOfficeSerializer,SubDivisionalOfficeSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from users.api.permissions import IsDivisionalOffice,IsSubDivisionalOffice

class DivisionalOfficeSignUpView(generics.GenericAPIView):
    serializer_class=DivisionalOfficeSignUpSerializer

    def post(self, request, *args, **kwargs):
        print(request)
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.save()
        offices = DivisionalOffice.objects.filter(user=user)
        
        return Response({
            "user":DivisionalOfficeSerializer(offices, many=True).data,
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
        offices = SubDivisionalOffice.objects.filter(user=user)
        data = SubDivisionalOfficeSerializer(offices, many=True).data  # Serialize queryset
        return Response({
            "user":data,
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
        print(token)
        data = None
        if user.is_divisional:
            offices = DivisionalOffice.objects.filter(user=user)
            data = DivisionalOfficeSerializer(offices, many=True).data  # Serialize queryset
        elif user.is_sub_divisional:
            offices = SubDivisionalOffice.objects.filter(user=user)
            data = SubDivisionalOfficeSerializer(offices, many=True).data  # Serialize queryset
        
        return Response({
            "user":data,
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
