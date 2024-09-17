from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from .models import *



CATEGORIES = [('', 'Select a category (optional)'), ("fashion", "Fashion"), ("electronics", "Electronics"), ("home & garden", "Home & Garden"), ("collectibles & art", "Collectibles & Art"), 
              ("sporting goods", "Sporting Goods"), ("toys & hobbies", "Toys & Hobbies"), ("motors", "Motors"), ("business & industrial", "Business & Industrial"), 
              ("health & beauty", "Health & Beauty"), ("music", "Music"), ("crafts", "Crafts"), ("antiques", "Antiques"), 
              ("books", "Books"), ("coins & paper money", "Coins & Paper Money"), ("computers/tablets & networking", "Computers/Tablets & Networking"), ("cameras & photo", "Cameras & Photo"), 
              ("cell phones & accessories", "cell phones & accessories"), ("jewelry & watches", "Jewelry & Watches"), ("travel", "travel"), ("baby", "Baby")] 



class NewCreateListingForm(forms.Form):

    title = forms.CharField(
        max_length=80,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter product name',
        }),
        required=True
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter product description',
            'rows': 4,
        }),
        required=True
    )

    current_bid = forms.DecimalField(
        max_digits=9,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter starting bid',
            'step': '1.00',
        }),
        required=True
    )

    category = forms.MultipleChoiceField(
        choices=CATEGORIES,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'size': '8'
        }),
        required=False  # Optional field
    )
    
    image_url = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter image URL (optional)',
        }),
        required=False  # Optional field
    )



def is_number(num):
    if "." in num and num.count('.') == 1:
        return num.replace('.', '').isdigit()

    elif "." not in num:
        return num.isdigit()
    
    else:
        return False




def index(request):
    # returns a list of objects, each object is a row
    active_listings = Auction_Listing.objects.filter(is_active=1)
    return render(request, "auctions/index.html", {
        "listings": active_listings
    })




def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")




def logout_view(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    logout(request)
    return HttpResponseRedirect(reverse("index"))




def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        except ValidationError as e:
            return render(request, "auctions/register.html", {
                "message": e
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")




def create_listing(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    # do backend check on the first three listings
    if request.method == "POST":
        form = NewCreateListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            starting_bid = form.cleaned_data['current_bid']
            categories = form.cleaned_data['category']
            image_url = form.cleaned_data['image_url']


            new_listing = Auction_Listing(
                owner=request.user,
                title=title,
                description=description,
                current_bid=starting_bid,
                image_url=image_url,
                is_active=1,  # Use 1 for active or True
            )
            new_listing.save()

            for name in categories:
                category = Categorie.objects.get(name=name)
                new_listing.categories.add(category)
            

            new_bid = Bid(listing=new_listing, bidder=request.user, bid=starting_bid)
            new_bid.save()

            return HttpResponseRedirect(reverse(index))
        
        else:
            return render(request, "auctions/create_listing.html", {
                "form": form,
                "message": "Invalid input",
            })


    return render(request, "auctions/create_listing.html", {
        "form": NewCreateListingForm()
    })




def view_listing(request):
    listing_id = request.GET.get("listing_id")

    listing = get_object_or_404(Auction_Listing, id=listing_id)
    num_bids = Bid.objects.filter(listing_id=listing_id).count() - 1
    comments = Comment.objects.filter(listing=listing_id)
    categories = listing.categories.all()

    if request.user.is_authenticated:
        user = request.user
        is_watch = listing in user.watched_listings.all()
    else:
        is_watch = False

    
    winner = listing.winner
    if winner:
        if request.user == winner:
            message = "Auction ended.\nYou won!"

            return render(request, "auctions/listing.html", {
                "listing": listing,
                "categories": categories,
                "num_bids": num_bids,
                "comments": comments,
                "is_watch": is_watch,
                "winner_win_message": message,

            })
        else:
            message = "Auction ended.\nThe winner is " + winner.username + "."

            return render(request, "auctions/listing.html", {
                "listing": listing,
                "categories": categories,
                "num_bids": num_bids,
                "comments": comments,
                "is_watch": is_watch,
                "other_win_message": message,
            })
    else:
        return render(request, "auctions/listing.html", {
                "listing": listing,
                "categories": categories,
                "num_bids": num_bids,
                "comments": comments,
                "is_watch": is_watch,
            })

    





def add_comment(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        text = request.POST.get("comment")
        listing_id = request.POST.get("listing_id")
        listing = get_object_or_404(Auction_Listing, id=listing_id)
        user = request.user
        num_bids = Bid.objects.filter(listing_id=listing_id).count() - 1
        comments = Comment.objects.filter(listing=listing_id)
        is_watch = listing in user.watched_listings.all()  
        categories = listing.categories.all()

        if not text:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "categories": categories,
                "num_bids": num_bids,
                "comments": comments,
                "is_watch": is_watch,
                "comment_message": "Comment cannot be empty",
            })

        if listing.owner.id == user.id:
            text = text + " (owner)"

        comment = Comment(comment=text, listing=listing, user=user)

        try:
            comment.save()
        except ValidationError:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "categories": categories,
                "num_bids": num_bids,
                "comments": comments,
                "is_watch": is_watch,
                "comment_message": "Comment cannot exceed 1000 characters",
            })
        
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "categories": categories,
            "num_bids": num_bids,
            "comments": comments,
            "is_watch": is_watch
        })
    



def close_auction(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        listing_id = request.POST.get("listing_id")
        listing = get_object_or_404(Auction_Listing, id=listing_id)
        listing.is_active = 0
        listing.save()
        user = request.user
        num_bids = Bid.objects.filter(listing_id=listing_id).count() - 1
        is_watch = listing in user.watched_listings.all()
        comments = Comment.objects.filter(listing=listing_id)
        categories = listing.categories.all()

        if num_bids == 0:
            return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "num_bids": num_bids,
                    "comments": comments,
                    "is_watch": is_watch,
                    "categories": categories,
                })

        listing_bids = Bid.objects.filter(listing_id=listing_id).order_by('-bid')
        highest_bid = listing_bids[0]
        winner = highest_bid.bidder
        listing.winner = winner
        listing.save()

        message = "Auction ended.\nThe winner is " + winner.username + "."

        return render(request, "auctions/listing.html", {
                "listing": listing,
                "num_bids": num_bids,
                "comments": comments,
                "is_watch": is_watch,
                "categories": categories,
                "other_win_message": message,
            })
  





# TODO categories viewing

# TODO create a Purchases page that displays all listings that the user won



def add_bid(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        amount = request.POST.get("bid")
        listing_id = request.POST.get("listing_id")
        listing = get_object_or_404(Auction_Listing, id=listing_id)
        user = request.user
        num_bids = Bid.objects.filter(listing_id=listing_id).count() - 1
        is_watch = listing in user.watched_listings.all()
        comments = Comment.objects.filter(listing=listing_id)
        categories = listing.categories.all()

        if amount == "":
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "num_bids": num_bids,
                "comments": comments,
                "is_watch": is_watch,
                "categories": categories,
                "bid_empty": "Please enter a bid",
            })
        
        elif not is_number(amount):
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "num_bids": num_bids,
                "comments": comments,
                "is_watch": is_watch,
                "categories": categories,
                "bid_not_number": "Enter a number please",
            })
        
        

        listing_bids = Bid.objects.filter(listing_id=listing_id).order_by('-bid')
        current_price = listing_bids[0].bid
        

        
        if num_bids == 0:
            if float(amount) < current_price:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "num_bids": num_bids,
                    "comments": comments,
                    "is_watch": is_watch,
                    "categories": categories,
                    "is_bid_success": False,
                    "is_first": True,
                })

            else:
                new_bid = Bid(listing=listing, bidder=request.user, bid=amount)
                new_bid.save()
                listing.current_bid = amount
                listing.save()

                user = request.user
                watch_list = user.watched_listings.all()

                if listing not in watch_list:
                    user.watched_listings.add(listing)
                
                is_watch = listing in user.watched_listings.all()

                text = "I placed a bid of $" + amount + "."

                comment = Comment(comment=text, listing=listing, user=user)
                comment.save()

                num_bids = Bid.objects.filter(listing_id=listing_id).count() - 1

                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "num_bids": num_bids,
                    "comments": comments,
                    "is_watch": is_watch,
                    "categories": categories,
                    "is_bid_success": True,
                })
        else:
            if float(amount) <= current_price:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "num_bids": num_bids,
                    "comments": comments,
                    "is_watch": is_watch,
                    "categories": categories,
                    "is_bid_success": False,
                    "is_first": False,
                })

            else:
                new_bid = Bid(listing=listing, bidder=request.user, bid=amount)
                new_bid.save()
                listing.current_bid = amount
                listing.save()

                user = request.user
                watch_list = user.watched_listings.all()

                if listing not in watch_list:
                    user.watched_listings.add(listing)
                
                is_watch = listing in user.watched_listings.all()

                text = "I placed a bid of $" + amount + "."

                comment = Comment(comment=text, listing=listing, user=user)
                comment.save()

                num_bids = Bid.objects.filter(listing_id=listing_id).count() - 1

                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "num_bids": num_bids,
                    "comments": comments,
                    "is_watch": is_watch,
                    "categories": categories,
                    "is_bid_success": True,
                })







def add_watch(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        listing_id = request.POST.get("listing_id")
        listing = get_object_or_404(Auction_Listing, id=listing_id)
        user = request.user
        user.watched_listings.add(listing)

        num_bids = Bid.objects.filter(listing_id=listing_id).count() - 1
        comments = Comment.objects.filter(listing=listing_id)
        is_watch = listing in user.watched_listings.all()
        categories = listing.categories.all()

        return render(request, "auctions/listing.html", {
            "listing": listing,
            "num_bids": num_bids,
            "comments": comments,
            "is_watch": is_watch,
            "categories": categories,
        })
    


def remove_watch(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        listing_id = request.POST.get("listing_id")
        listing = get_object_or_404(Auction_Listing, id=listing_id)
        user = request.user
        user.watched_listings.remove(listing)


        num_bids = Bid.objects.filter(listing_id=listing_id).count() - 1
        comments = Comment.objects.filter(listing=listing_id)
        is_watch = listing in user.watched_listings.all()
        categories = listing.categories.all()

        return render(request, "auctions/listing.html", {
            "listing": listing,
            "num_bids": num_bids,
            "comments": comments,
            "is_watch": is_watch,
            "categories": categories,
        })




def view_watch_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    user = request.user
    watch_list = user.watched_listings.all()
    return render(request, "auctions/watch_list.html", {
        "listings": watch_list
    })



def view_my_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    listings = Auction_Listing.objects.filter(owner=request.user)
    return render(request, "auctions/my_list.html", {
        "listings": listings
    })
