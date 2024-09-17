from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watched_listings = models.ManyToManyField('Auction_Listing', blank=True, related_name="watched_users")

class Auction_Listing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=80)
    description = models.TextField()
    current_bid = models.DecimalField(max_digits=9, decimal_places=2)
    datetime = models.DateTimeField(auto_now_add=True)
    image_url = models.TextField(blank=True)
    categories = models.ManyToManyField('Categorie', related_name='category_listings', blank = True)
    is_active = models.IntegerField()
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='purchases')

class Bid(models.Model):
    listing = models.ForeignKey(Auction_Listing, on_delete=models.CASCADE, related_name='listing_bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_bids')
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    datetime = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    comment = models.TextField(max_length=1000)
    datetime = models.DateTimeField(auto_now_add=True)
    listing = models.ForeignKey(Auction_Listing, on_delete=models.CASCADE, related_name='listing_comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')


class Categorie(models.Model):
    name = models.CharField(max_length=80)

