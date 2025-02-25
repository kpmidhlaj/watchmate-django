import logging
from venv import logger
import logging

from django.db.models import Avg
from rest_framework import status, generics, viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from user_app.api.throtlling import ReviewListThrottle, ReviewCreateThrottle
from watchlist_app.api.pagination import WatchListPagination, LOPagination, WatchListCPagination
from watchlist_app.api.permissions import IsAdminOrReadOnly, IsReviewUserOrReadOnly
from watchlist_app.api.serializers import (WatchlistSerializer, StreamPlatformSerializer, ReviewSerializer)
from watchlist_app.models import (Watchlist, StreamPlatform, Review)


# ////function base view
# @api_view( ['GET', 'POST'] )
# def movie_list(request):
#     if request.method == 'GET':
#         try:
#             movies = Movie.objects.all()
#         except Movie.DoesNotExist:
#             return Response ({'message': 'No data Found'},status=status.HTTP_400_BAD_REQUEST )
#         serializer = MovieSerializer(movies, many=True)
#         return Response(serializer.data)
#
#     elif request.method == 'POST':
#         serializer = MovieSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors,status = status.HTTP_400_BAD_REQUEST)
#
# @api_view(['GET', 'PUT', 'DELETE'])
# def movie_detail(request, pk):
#     if request.method == 'GET':
#         try:
#             movie = Movie.objects.get(pk=pk)
#         except Movie.DoesNotExist:
#             return Response ({'message': 'Movie not found'},status=status.HTTP_400_BAD_REQUEST )
#         serializer = MovieSerializer(movie)
#         return Response(serializer.data)
#
#     elif request.method == 'PUT':
#         movie = Movie.objects.get(pk=pk)
#         serializer = MovieSerializer( instance=movie, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors,status= status.HTTP_400_BAD_REQUEST)
#
#     elif request.method == 'DELETE':
#         movie = Movie.objects.get(pk=pk)
#         movie.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


class UserReview(generics.ListAPIView):
    serializer_class = ReviewSerializer

    # def get_queryset(self):
    #     username = self.kwargs.get('username')
    #     return Review.objects.filter(review_user__username=username)

    def get_queryset(self):
        username = self.request.GET.get('username')
        if not username:
            return Review.objects.none()
        else:
            return Review.objects.filter(review_user__username=username)


# Concreate view

class ReviewList(generics.ListAPIView):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    throttle_classes = [ReviewListThrottle, AnonRateThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['review_user__username', 'active']

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Review.objects.filter(watchlist=pk)

    def permission_denied(self, request, message=None, code=None):
        raise PermissionDenied(detail="You do not have permission to modify the review list.")


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    permission_classes = [IsReviewUserOrReadOnly]
    serializer_class = ReviewSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'review-detail'

    def permission_denied(self, request, message=None, code=None):
        raise PermissionDenied(detail="You do not have permission to modify the review.")


class ReviewCreate(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReviewCreateThrottle, AnonRateThrottle]

    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        watchlist = get_object_or_404(Watchlist, pk=pk)
        review_user = self.request.user

        # Check if the user has already reviewed this watchlist
        existing_review = Review.objects.filter(watchlist=watchlist, review_user=review_user, active=True).first()

        new_rating = serializer.validated_data['rating']
        if new_rating > 5 or new_rating < 0:
            raise ValidationError({"message": "Rating must be between 0 and 5."})

        if existing_review:
            # If the review exists, update it instead of creating a new one
            existing_review.rating = new_rating
            existing_review.description = serializer.validated_data.get('description', existing_review.description)
            existing_review.save()

            # Recalculate the average rating
            all_reviews = Review.objects.filter(watchlist=watchlist, active=True)
            watchlist.avg_rating = all_reviews.aggregate(Avg('rating'))['rating__avg'] or 0
            watchlist.save()

            raise ValidationError(
                {"message": "Your review has been updated."})

        else:

            if watchlist.number_rating == 0:
                watchlist.avg_rating = new_rating
            else:
                total_rating_sum = watchlist.avg_rating * watchlist.number_rating
                watchlist.avg_rating = (total_rating_sum + new_rating) / (watchlist.number_rating + 1)

            watchlist.number_rating += 1
            watchlist.save()

            serializer.save(watchlist=watchlist, review_user=review_user)


# Generic View

# class ReviewDetail(mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,generics.GenericAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)
#
#     def put(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)
#
#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)
#
# class ReviewList(mixins.ListModelMixin,mixins.CreateModelMixin,generics.GenericAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)

class WatchListGV(generics.ListAPIView):
    queryset = Watchlist.objects.all()
    serializer_class = WatchlistSerializer
    pagination_class = WatchListCPagination
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ['avg_rating']


# ////class base view


class WatchListAv(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        movies = Watchlist.objects.all()
        serializer = WatchlistSerializer(movies, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WatchlistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WatchDetailAV(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk):
        try:
            movie = Watchlist.objects.get(pk=pk)
        except Watchlist.DoesNotExist:
            return Response({'message': 'Movie not found'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = WatchlistSerializer(movie)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            movie = Watchlist.objects.get(pk=pk)
        except Watchlist.DoesNotExist:
            return Response({'message': 'Movie not found'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = WatchlistSerializer(instance=movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            movie = Watchlist.objects.get(pk=pk)
        except Watchlist.DoesNotExist:
            return Response({'message': 'Movie not found'}, status=status.HTTP_400_BAD_REQUEST)
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Model Viewset
class StreamPlatformVS(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = StreamPlatform.objects.all()
    serializer_class = StreamPlatformSerializer

# viewSet and Router
# class StreamPlatformVS(viewsets.ViewSet):
#     def list(self, request):
#         queryset = StreamPlatform.objects.all()
#         serializer = StreamPlatformSerializer(queryset, many=True)
#         return Response(serializer.data)
#
#     def retrieve(self, request, pk=None):
#         queryset = StreamPlatform.objects.all()
#         watchlist = get_object_or_404(queryset, pk=pk)
#         serializer = StreamPlatformSerializer(watchlist)
#         return Response(serializer.data)
#
#     def create(self, request):
#         serializer = StreamPlatformSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class StreamPlatformAv(APIView):
#     def get(self, request):
#         platforms = StreamPlatform.objects.all()
#         serializer = StreamPlatformSerializer(platforms, many=True,context={'request': request})
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = StreamPlatformSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class StreamPlatformDetailAV(APIView):
#     def get(self, request, pk):
#         try:
#             platform = StreamPlatform.objects.get(pk=pk)
#         except StreamPlatform.DoesNotExist:
#             return Response({'message': 'Platform not found'}, status=status.HTTP_400_BAD_REQUEST)
#         serializer = StreamPlatformSerializer(platform,context= {'request':request})
#         return Response(serializer.data)
#
#     def put(self, request, pk):
#         try:
#             platform = StreamPlatform.objects.get(pk=pk)
#         except StreamPlatform.DoesNotExist:
#             return Response({'message': 'Platform not found'}, status=status.HTTP_400_BAD_REQUEST)
#         serializer = StreamPlatformSerializer(instance=platform, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk):
#         try:
#             platform = StreamPlatform.objects.get(pk=pk)
#         except StreamPlatform.DoesNotExist:
#             return Response({'message': 'Platform not found'}, status=status.HTTP_400_BAD_REQUEST)
#         platform.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
