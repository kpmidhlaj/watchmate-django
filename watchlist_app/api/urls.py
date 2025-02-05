from django.urls import path, include
from rest_framework.routers import DefaultRouter

from watchlist_app.api.views import (WatchListAv,WatchDetailAV,ReviewList, ReviewDetail, ReviewCreate, StreamPlatformVS)

router = DefaultRouter()
router.register('stream', StreamPlatformVS, basename='streamplatform')


urlpatterns = [
    path('list/', WatchListAv.as_view(), name='movie-list'),
    path('<int:pk>/', WatchDetailAV.as_view(), name='movie-detail'),
    # path('stream/', StreamPlatformAv.as_view(), name='stream-list'),
    # path('stream/<int:pk>/', StreamPlatformDetailAV.as_view(), name='stream-detail'),
    path('', include(router.urls)),
    # Review
    # path('review/',ReviewList.as_view(),name ='review-list'),
    # path('review/<int:pk>',ReviewDetail.as_view(),name='review-detail'),
    path('stream/<int:pk>/review/', ReviewList.as_view(), name='review-list'),
    path('stream/<int:pk>/review-create/', ReviewCreate.as_view(), name='review-create'),
    path('stream/review/<int:pk>/', ReviewDetail.as_view(), name='review-detail'),
]
