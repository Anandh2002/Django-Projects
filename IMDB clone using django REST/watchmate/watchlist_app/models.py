from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from django.contrib.auth.models import User



class StreamPlatform(models.Model):
    name=models.CharField(max_length=30)
    description=models.CharField(max_length=150)
    website=models.URLField(max_length=100)
    def __str__(self):
        return self.name 


class WatchList(models.Model):
    title=models.CharField(max_length=50)
    storyline=models.TextField(max_length=500)
    active=models.BooleanField(default=True)
    platform=models.ForeignKey(StreamPlatform,on_delete=models.CASCADE,related_name="watchlist")
    avg_rating=models.FloatField(default=0)
    number_of_ratings=models.IntegerField(default=0)
    created=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    
class Review(models.Model):
    review_user=models.ForeignKey(User,on_delete=models.CASCADE)
    rating=models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    description=models.CharField(max_length=200,null=True)
    watchlist=models.ForeignKey(WatchList,on_delete=models.CASCADE,related_name="reviews")
    created=models.DateTimeField(auto_now_add=True)
    update=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.rating)+" | "+ self.watchlist.title
    
