from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Auction_Listing)
admin.site.register(User)
admin.site.register(Categorie)
admin.site.register(Bid)
admin.site.register(Comment)