from rest_framework import serializers
from watchlist_app.models import WatchList,StreamPlatform,Review





class ReviewSerializer(serializers.ModelSerializer):
    review_user=serializers.StringRelatedField(read_only=True)
    class Meta:
        model=Review
        # fields="__all__"
        exclude=('watchlist',)

class WatchListSerializer(serializers.ModelSerializer):
    reviews=ReviewSerializer(many=True,read_only=True)
    class Meta:
        model=WatchList
        fields="__all__"
        
        
class StreamPlatformSerializer(serializers.HyperlinkedModelSerializer):
    watchlist=WatchListSerializer(many=True,read_only=True)
    class Meta:
        model=StreamPlatform
        fields="__all__"
        
        


    # def validate_name(self,value): # feild level validation
    #     if len(value)<2:
    #         raise serializers.ValidationError("Name is too short !!")
    #     return value

    # def validate(self,data): #object level validation
    #     if data['name']==data['description']:
    #         raise serializers.ValidationError("Name and Descriptions should not be same !!")
    #     return data

    # def get_len_name(self,object):
    #     return len(object.name)

    
# def name_length(value):
#     if len(value)<2:
#         raise serializers.ValidationError("Name is too short !!")
#     return value

# class WatchListSerializer(serializers.Serializer):    
#     id = serializers.IntegerField(read_only=True)
#     name=serializers.CharField(validators=[name_length])
#     description=serializers.CharField()
#     active=serializers.BooleanField()
    
#     def create(self, validated_data):
#         return WatchList.objects.create(**validated_data)
    
#     def update(self, instance,validated_data):
#         instance.name=validated_data.get('name',instance.name)
#         instance.description=validated_data.get('description',instance.description)
#         instance.active=validated_data.get('active',instance.active)
#         instance.save()
#         return instance

# #************ Validators for Serializers **************************************8

#     # def validate_name(self,value): # feild level validation
#     #     if len(value)<2:
#     #         raise serializers.ValidationError("Name is too short !!")
#     #     return value

#     def validate(self,data): #object level validation
#         if data['name']==data['description']:
#             raise serializers.ValidationError("Name and Descriptions should not be same !!")
#         return data