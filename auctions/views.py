from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import *
from django.contrib.auth.decorators import login_required

from .models import User
from .forms import  ListingForm, CommentForm, BidForm

def index(request):
    listings = Listing.objects.filter(is_active=True)
    for listing in listings:
        listing.current_bid, current_bid_user = find_current_bid_for_listing(id=listing.id)
    return render(request, "auctions/index.html", {
        'listings': listings,
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
        login(request, user)
        print('ok')
        Watchlist.objects.create(user=user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")




def show_watchlist(request):
    user = request.user
    watchlist = Watchlist.objects.get(user=user)
    listings = watchlist.listing.all()
    for listing in listings:
        listing.current_bid, current_bid_user = find_current_bid_for_listing(id=listing.id)
    return render(request, 'auctions/watchlist.html', {
        'listings': listings,
    })

@login_required
def add_to_watchlist(request, id):
    listing = get_object_or_404(Listing, pk=id)
    user = request.user
    watchlist = Watchlist.objects.get(user=user)
    watchlist.listing.add(listing)
    return show_listing(request=request, id=id)



def remove_from_watchlist(request, id):
    listing = get_object_or_404(Listing, pk=id)
    user = request.user
    watchlist = Watchlist.objects.get(user=user)
    if listing in watchlist.listing.all():
        watchlist.listing.remove(listing)
    return show_listing(request=request, id=id)



def show_categories(request):
    categories = Category.objects.all()
    return render(request, 'auctions/categories.html', {

        'categories': categories,
    })


def show_listings_in_category(request, name):
    category = get_object_or_404(Category, name=name)
    listings_in_category = Listing.objects.filter(category=category, is_active=True)
    for listing in listings_in_category:
        listing.current_bid, current_bid_user = find_current_bid_for_listing(id=listing.id)
    return render(request, 'auctions/listings_in_category.html', {
        'category': category,
        'listings_in_category': listings_in_category,
    })


def show_listing(request, id):
    form_bid = BidForm(None)
    comment_form_is_active = False
    user = request.user
    listing = get_object_or_404(Listing, pk=id)
    listing.current_bid, current_bid_user = find_current_bid_for_listing(id=listing.id)
    if current_bid_user != None:
        if request.user == current_bid_user:
            winner = 'You! Congratulations!'
        else:
            winner = current_bid_user
    else:
        winner = 'Nobody. Nobody made any bids.'
    is_active = listing.is_active
    comments = Comment.objects.filter(listing=listing)
    is_in_watchlist = False
    if user.is_authenticated:
        watchlist = Watchlist.objects.get(user=user)
        if listing in watchlist.listing.all():
            is_in_watchlist = True
    return render(request, 'auctions/listing.html', {
        'listing': listing,
        'comments': comments,
        'is_in_watchlist': is_in_watchlist,
        'comment_form_is_active': comment_form_is_active,
        'form_bid': form_bid,
        'is_active': is_active,
        'winner': winner,
        'is_creator': bool(request.user == listing.creator_user)
    })
@login_required
def create_listing(request):
    user = request.user
    form = ListingForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        listing = form.save(commit=False)
        listing.creator_user = user
        listing.save()
        return redirect(index)

    return render(request, 'auctions/create_listing.html', {
        'form': form,
    })

@login_required
def leave_comment(request, id):
    comment_form_is_active = True
    user = request.user
    listing = get_object_or_404(Listing, pk=id)
    comments = Comment.objects.filter(listing=listing)
    is_in_watchlist = False
    watchlist = Watchlist.objects.get(user=user)
    if listing in watchlist.listing.all():
        is_in_watchlist = True
    form = CommentForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = user
        comment.listing = listing
        comment.save()
        comment_form_is_active = False
    return render(request, 'auctions/listing.html', {
        'listing': listing,
        'comments': comments,
        'is_in_watchlist': is_in_watchlist,
        'comment_form_is_active': comment_form_is_active,
        'form': form,
    })

@login_required
def make_bid(request, id):
    listing_current_bid, current_bid_user = find_current_bid_for_listing(id)
    user = request.user
    listing = get_object_or_404(Listing, pk=id)
    form_bid = BidForm(request.POST)
    if form_bid.is_valid():
        bid = form_bid.save(commit=False)
        if listing_current_bid == 0 and bid.bid_value != 0:
            if bid.bid_value >= listing.starting_bid:
                listing_current_bid = bid.bid_value
                bid.user = user
                bid.listing = listing
                bid.save()
            else:
                return HttpResponse('<h4 style="color: red">ERROR. The bid must be at least as large as the starting bid! </h4>')
        elif listing_current_bid != 0 and bid.bid_value != 0:
            if bid.bid_value > listing_current_bid:
                listing_current_bid = bid.bid_value
                bid.user = user
                bid.listing = listing
                bid.save()
            else:
                return HttpResponse('<h4 style="color: red">ERROR. The bid must be greater than the current bid! </h4>')
    listing.current_bid = listing_current_bid
    listing.save()
    return show_listing(request=request, id=id)



def find_current_bid_for_listing(id):
    listing = get_object_or_404(Listing, pk=id)
    bids_for_listing = Bid.objects.filter(listing=listing)
    current_bid_user = None
    if not bids_for_listing:
        listing.current_bid = 0
    for bid in bids_for_listing:
        if bid.bid_value >= listing.starting_bid:
            listing.current_bid = bid.bid_value
            current_bid_user = bid.user
    return listing.current_bid, current_bid_user


def find_user_won_auction(id):
    pass

def close_auction(request, id):
    print(request)
    listing = get_object_or_404(Listing, pk=id)
    listing.current_bid, current_bid_user = find_current_bid_for_listing(id=listing.id)
    if request.method == 'POST':
        listing.is_active = False
        listing.save()
        return show_listing(request=request, id=id)
    return render(request, 'auctions/closing_confirmation.html', {
        'listing': listing,
        'winner': current_bid_user,
        'listing.current_bid': listing.current_bid,
    })