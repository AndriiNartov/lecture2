from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField('Category name', max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Listing(models.Model):
    is_active = models.BooleanField(null=False, blank=False, default=True)
    creator_user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    title = models.CharField(max_length=50, blank=False)
    description = models.TextField(max_length=200)
    image = models.ImageField(upload_to='images', null=True, blank=True)
    starting_bid = models.DecimalField(max_digits=9,decimal_places=0, default=0)
    current_bid = models.DecimalField(max_digits=9,decimal_places=0, default=0)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True)
    watchlist = models.ForeignKey('Watchlist', blank=True, null=True, on_delete=models.CASCADE, related_name='related_listing')

    def __str__(self):
        return self.title


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid_value = models.DecimalField('Your bid', max_digits=9, decimal_places=0)

    def __str__(self):
        return f'User "{self.user.username}" makes a bid {self.bid_value}$ for "{self.listing.title}"'


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    comment_content = models.TextField(max_length=500, blank=True, null=True)


    def __str__(self):
        return f'User "{self.user.username}" leaves a comment for "{self.listing.title}"'


class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    listing = models.ManyToManyField(Listing, related_name='related_watchlist', null=True, blank=True)

    def __str__(self):
        return f'Watchlist of user {self.user.username}'






