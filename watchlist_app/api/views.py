import logging
from venv import logger
import logging

from django.db.models import Avg
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from watchlist_app.api.permissions import AdminOrReadOnly, ReviewUserOrReadOnly
from watchlist_app.api.serializers import (WatchlistSerializer,StreamPlatformSerializer,ReviewSerializer)
from watchlist_app.models import (Watchlist,StreamPlatform,Review)


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

# Concreate view

class ReviewList(generics.ListAPIView):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [AdminOrReadOnly]

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Review.objects.filter(watchlist=pk)


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    permission_classes = [ReviewUserOrReadOnly]
    serializer_class = ReviewSerializer

class ReviewCreate(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        watchlist = get_object_or_404(Watchlist, pk=pk)
        review_user = self.request.user

        logging.info(f"Checking review for user {review_user} on watchlist {watchlist.pk}")

        # Ensure user cannot submit multiple reviews
        if Review.objects.filter(watchlist=watchlist, review_user=review_user, active=True).exists():
            logging.info(f"Review already exists for user {review_user} on watchlist {watchlist.pk}")
            raise ValidationError("You have already reviewed this watchlist.")

        # Calculate new rating
        new_rating = serializer.validated_data['rating']

        if watchlist.number_rating == 0:
            watchlist.avg_rating = new_rating
        else:
            total_rating_sum = watchlist.avg_rating * watchlist.number_rating
            watchlist.avg_rating = (total_rating_sum + new_rating) / (watchlist.number_rating + 1)

        watchlist.number_rating += 1
        watchlist.save()

        logging.info(
            f"Updated Watchlist ({watchlist.pk}) ratings: avg_rating = {watchlist.avg_rating}, number_rating = {watchlist.number_rating}")

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

# ////class base view

class WatchListAv(APIView):
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

