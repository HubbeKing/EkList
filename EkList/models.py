from __future__ import unicode_literals
import datetime
from collections import OrderedDict

from django.contrib.auth.models import User
from django.db import models


class Auction(models.Model):
    title = models.CharField(max_length=32)
    description = models.TextField()

    created = models.DateTimeField()
    modified = models.DateTimeField(null=True, blank=True)

    creator_username = models.CharField(max_length=64)
    minimum_bid = models.FloatField()
    expires = models.DateTimeField()

    current_bid = models.FloatField(default=0.0)
    current_bidder_username = models.CharField(max_length=64, blank=True)
    current_bid_timestamp = models.DateTimeField(null=True, blank=True)

    bidders = models.ManyToManyField(User, blank=True)

    is_banned = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("ban_auction", "Can ban any auction"),
        )

    @classmethod
    def get_by_id(cls, id_number):
        return cls.objects.get(id=id_number)

    @classmethod
    def exists(cls, id_number):
        return len(cls.objects.filter(id=id_number)) > 0

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def has_bid(cls, id_number):
        if cls.objects.get(id=id_number).current_bid != 0.0:
            return True

    @classmethod
    def is_valid(cls, id_number):
        auction = cls.objects.get(id=id_number)
        tzinfo = auction.expires.tzinfo
        if not auction.is_banned and auction.expires > datetime.datetime.now(tzinfo):
            return True
        return False

    @classmethod
    def is_expired(cls, id_number):
        auction = cls.objects.get(id=id_number)
        tzinfo = auction.expires.tzinfo
        if auction.expires < datetime.datetime.now(tzinfo):
            return True
        return False

    @classmethod
    def get_all_expired(cls):
        auctions = cls.objects.all()
        expired_auctions = []
        for auction in auctions:
            if auction.is_expired(auction.id):
                expired_auctions.append(auction)
        return expired_auctions

    @classmethod
    def get_all_valid(cls):
        auctions = cls.objects.all()
        valid_auctions = []
        for auction in auctions:
            if auction.is_valid(auction.id):
                valid_auctions.append(auction)
        return valid_auctions

    @classmethod
    def get_by_creator(cls, username):
        return cls.objects.filter(creator_username=username)

    @classmethod
    def get_by_bidder(cls, username):
        return cls.objects.filter(current_bidder_username=username)

    @classmethod
    def get_time_remaining(cls, auction_id):
        if cls.is_expired(auction_id):
            return "Auction expired."
        auction = cls.objects.get(id=auction_id)
        tzinfo = auction.expires.tzinfo
        timedelta = auction.expires - datetime.datetime.now(tzinfo)
        return Auction.timedelta_to_string(timedelta)

    @staticmethod
    def timedelta_to_string(time_delta, resolution='m'):
        d = OrderedDict()
        d['days'] = time_delta.days
        d['hours'], rem = divmod(time_delta.seconds, 3600)
        if resolution == 'm' or resolution == 's':
            d['minutes'], seconds = divmod(rem, 60)
            if resolution == 's':
                d['seconds'] = seconds

        def lex(duration_word, duration):
            if duration == 1:
                return '{0} {1}'.format(duration, duration_word[:-1])
            else:
                return '{0} {1}'.format(duration, duration_word)

        delta_string = ' '.join([lex(word, number) for word, number in d.iteritems() if number > 0])
        return delta_string if len(delta_string) > 0 else 'seconds'


class UserData(models.Model):
    username = models.CharField(max_length=64)
    preferred_language = models.CharField(max_length=8)  # store preferred language as language code (en_US)

    @classmethod
    def exists(cls, user):
        return len(cls.objects.filter(username=user)) > 0

    @classmethod
    def get_user_data(cls, user):
        return cls.objects.get(username=user)

    @classmethod
    def get_language(cls, user):
        return cls.objects.get(username=user).preferred_language
