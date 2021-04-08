from django.forms import ModelForm
from .models import *


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'image', 'starting_bid', 'category']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_content']


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['bid_value']
