from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated # type: ignore
from rest_framework import permissions
from rest_framework.throttling import UserRateThrottle,AnonRateThrottle,ScopedRateThrottle

from watchlist_app.models import *
from watchlist_app.api.permissions import IsAdminOrReadOnly,IsReviewUserOrReadOnly
from watchlist_app.api.serializers import *
from watchlist_app.api.throttling import ReviewcreateThrottle,ReviewListThrottle

from django.shortcuts import get_object_or_404

   
class WatchListAV(APIView):
    permission_classes = [IsAdminOrReadOnly]
    
    def get(self,request):
        
        WatchLists=WatchList.objects.all()
        serialized_data=WatchListSerializer(WatchLists,many=True)
        return Response(serialized_data.data)

    def post(self,request):
        serializer=WatchListSerializer(data=request.data) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=201)
        else:
            return Response(serializer.errors,status=400)

class WatchListDetailsAV(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self,request,pk):
        try:
            watchlist=WatchList.objects.get(pk=pk)
        except WatchList.DoesNotExist:
            return Response({'error :  Not Found'},status=status.HTTP_404_NOT_FOUND)
        serialized_data=WatchListSerializer(watchlist)
        return Response(serialized_data.data)

    def put(self,request,pk):
        watchlist=WatchList.objects.get(pk=pk)
        serializer=WatchListSerializer(watchlist,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=201)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk):
        watchlist=WatchList.objects.get(pk=pk)
        watchlist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class StreamPlatformVS(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = StreamPlatform.objects.all()
    serializer_class = StreamPlatformSerializer
    
class ReviewCreate(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReviewcreateThrottle, AnonRateThrottle]
    
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        return Review.objects.all()
    
    def perform_create(self, serializer):
        pk=self.kwargs.get('pk')
        watchlist=WatchList.objects.get(pk=pk)
        review_user=self.request.user
        review_queryset=Review.objects.filter(watchlist=watchlist,review_user=review_user)
        if review_queryset.exists():
            raise ValidationError("You have already reviewed this movie")
        
        if watchlist.avg_rating==0:
            watchlist.avg_rating=serializer.validated_data['rating']
        else:
            watchlist.avg_rating=(watchlist.avg_rating+serializer.validated_data['rating'])/2
            
        watchlist.number_of_ratings=watchlist.number_of_ratings+1
        watchlist.save()
            
        serializer.save(watchlist=watchlist,review_user=review_user)

class ReviewList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReviewListThrottle, AnonRateThrottle]
    serializer_class = ReviewSerializer    
    def get_queryset(self):
        pk=self.kwargs['pk']
        return Review.objects.filter(watchlist=pk)
    
class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsReviewUserOrReadOnly]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope='review-detail'
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


#************************ Class based View ***********************************************************************
# class ReviewList(mixins.ListModelMixin,
#                   mixins.CreateModelMixin,
#                   generics.GenericAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)
    
    
# class ReviewDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
#     queryset=Review.objects.all()
#     serializer_class = ReviewSerializer
    
#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)
    
    



# class StreamPlatformAV(APIView):

#     def get(self,request):
#         platform=StreamPlatform.objects.all()
#         serialized_data=StreamPlatformSerializer(platform,many=True,context={'request': request})
#         return Response(serialized_data.data)

#     def post(self,request):
#         serializer=StreamPlatformSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data,status=201)
#         else:
#             return Response(serializer.errors,status=400)

# class StreamPlatformDetailsAV(APIView):

#     def get(self,request,pk):
#         try:
#             platform=StreamPlatform.objects.get(pk=pk)
#         except StreamPlatform.DoesNotExist:
#             return Response({'error :  Not Found'},status=status.HTTP_404_NOT_FOUND)
#         serialized_data=StreamPlatformSerializer(platform,context={'request': request})
#         return Response(serialized_data.data)

#     def put(self,request,pk):
#         platform=StreamPlatform.objects.get(pk=pk)
#         serializer=StreamPlatformSerializer(platform,data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data,status=201)
#         else:
#             return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

#     def delete(self,request,pk):
#         platform=StreamPlatform.objects.get(pk=pk)
#         platform.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    
    
# class StreamPlatformVS(viewsets.ViewSet):
    
#     def list(self, request):
#         queryset = StreamPlatform.objects.all()
#         serializer = StreamPlatformSerializer(queryset, many=True,context={'request': request})
#         return Response(serializer.data)

#     def retrieve(self, request, pk=None):
#         queryset = StreamPlatform.objects.all()
#         watchlist = get_object_or_404(queryset, pk=pk)
#         serializer = StreamPlatformSerializer(watchlist,context={'request': request})
#         return Response(serializer.data)


    



#********************** Function Based View *************************************************************************
# @api_view(['GET','POST'])
# def WatchList_list(request):
#     if request.method == 'GET':
#         WatchLists=WatchList.objects.all()
#         serialized_data=WatchListSerializer(WatchLists,many=True)
#         return Response(serialized_data.data)
    
#     elif request.method == 'POST':
#         serializer=WatchListSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data,status=201)
#         else:
#             return Response(serializer.errors,status=400)
            
        
# @api_view(['GET','PUT','DELETE'])
# def WatchList_details(request,pk):
#     if request.method == 'GET':
#         try:
#             WatchList=WatchList.objects.get(pk=pk)
#         except WatchList.DoesNotExist:
#             return Response({'error : WatchList Not Found'},status=status.HTTP_404_NOT_FOUND)
#         serialized_data=WatchListSerializer(WatchList)
#         return Response(serialized_data.data)
#     if request.method == 'PUT':
#         WatchList=WatchList.objects.get(pk=pk)
#         serializer=WatchListSerializer(WatchList,data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data,status=201)
#         else:
#             return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
#     if request.method=='DELETE':
#         WatchList=WatchList.objects.get(pk=pk)
#         WatchList.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
        
        
        

