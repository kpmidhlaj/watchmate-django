from  rest_framework import  serializers

from watchlist_app.models import Watchlist, StreamPlatform, Review


# serializers.serializers

#
# class MovieSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     name = serializers.CharField(validators=[name_length])
#     description = serializers.CharField()
#     active = serializers.BooleanField()
#
#     def create(self, validated_data):
#       return  Movie.objects.create(**validated_data)
#
#     def update(self, instance, validated_data):
#         instance.name = validated_data.get('name', instance.name)
#         instance.description = validated_data.get('description', instance.description)
#         instance.active = validated_data.get('active', instance.active)
#         instance.save()
#         return instance
#


def name_length(value):
    if len(value) < 2:
        raise serializers.ValidationError('Name is too short')
    else:
        return value

# ReviewSerializer
class ReviewSerializer(serializers.ModelSerializer):
    review_user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Review
        exclude = ['watchlist']
        # fields = '__all__'

# ModelSerializer
class WatchlistSerializer(serializers.ModelSerializer):
    title = serializers.CharField(validators=[name_length])
    reviews = ReviewSerializer(many=True, read_only=True)
    class Meta:
        model = Watchlist
        fields = '__all__'
        # // fields = ['name', 'description', 'active']
    # exclude = ['active']
    def validate(self,data):
        if data['title'] == data['description']:
            raise serializers.ValidationError('Name and description should be different')
        else:
            return data

class StreamPlatformSerializer(serializers.ModelSerializer):
    watchlist = WatchlistSerializer(many=True, read_only=True)

    class Meta:
        model = StreamPlatform
        fields = '__all__'
        extra_kwargs = {
            'url': {'view_name': 'stream-detail', 'lookup_field': 'pk'}
        }

