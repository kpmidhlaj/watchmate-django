from rest_framework import serializers
from watchlist_app.models import Watchlist, StreamPlatform, Review


def name_length(value):
    if len(value) < 2:
        raise serializers.ValidationError("Name is too short")
    return value


# Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    review_user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'

    def validate(self, data):
        user = self.context['request'].user  # Get the logged-in user
        watchlist = data['watchlist']  # Get the watchlist being reviewed

        # Check if the request is for update
        if self.instance is None:  # Only enforce for new reviews
            if Review.objects.filter(review_user=user, watchlist=watchlist).exists():
                raise serializers.ValidationError("You have already reviewed this watchlist.")

        return data


# Watchlist Serializer
class WatchlistSerializer(serializers.ModelSerializer):
    title = serializers.CharField(validators=[name_length])
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Watchlist
        fields = '__all__'

    def validate(self, data):
        if data['title'] == data['description']:
            raise serializers.ValidationError("Title and description should be different")
        return data


# StreamPlatform Serializer
class StreamPlatformSerializer(serializers.ModelSerializer):
    watchlist = WatchlistSerializer(many=True, read_only=True)

    class Meta:
        model = StreamPlatform
        fields = '__all__'
