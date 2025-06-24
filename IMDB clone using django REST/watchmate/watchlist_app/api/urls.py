from django.urls import path,include
from watchlist_app.api import views
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register('stream',views.StreamPlatformVS,basename='streamplatform')


urlpatterns = [
   path('list/', views.WatchListAV.as_view(),name='WatchList-list'),
   path('<int:pk>/',views.WatchListDetailsAV.as_view(),name='WatchList-details'),
   # path('stream/', views.StreamPlatformAV.as_view(),name='streamplatform-list'),
   # path('stream/<int:pk>',views.StreamPlatformDetailsAV.as_view(),name='streamplatform-detail'),
   # path('review/', views.ReviewList.as_view(),name='review-list'),
   # path('review/<int:pk>/', views.ReviewDetail.as_view(),name='review-detail'),
   path('',include(router.urls)),
   path('<int:pk>/review/', views.ReviewList.as_view(),name='review-list'),
   path('review/<int:pk>/',views.ReviewDetail.as_view(),name='review-detail'),
   path('<int:pk>/review-create/',views.ReviewCreate.as_view(),name='review-create'),
   
   
   
]
