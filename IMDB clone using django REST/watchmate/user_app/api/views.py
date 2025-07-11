
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
# from rest_framework_simplejwt.tokens import RefreshToken

# from user_app import models
from user_app.api.serializers import RegisterationSerializer


@api_view(['POST',]) 
def registeration_view(request):   
    if request.method=='POST':
        serializer=RegisterationSerializer(data=request.data)
        data={}
        if serializer.is_valid():
            account=serializer.save()
            data['register']='New user registered !'
            data['username']=account.username
            data['email']=account.email
            # refresh = RefreshToken.for_user(account)
            token=Token.objects.get(user=account)
            # data['token']={
            #                 'refresh': str(refresh),
            #                 'access': str(refresh.access_token),
            #                 }                      
        else:
            data=serializer.errors
        return Response(data)
    
@api_view(['POST',]) 
def logout_view(request):
    if request.method=='POST':
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
    
        