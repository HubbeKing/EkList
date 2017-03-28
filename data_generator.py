from django.contrib.auth.models import User
from EkList.models import Auction
import datetime
import pytz


def populate():
    """
    This fills the EkList Django database with 99 users, and 1 auction for each of them.
    It then adds a single bid for 1/7th of those auctions, from 6 different users (id 1-6)
    It also creates an admin account.
    Please not that this script has to be run from the Django python shell, so Django knows which app settings to use.
    Test data was dumped to fixture with manage.py dumpdata --natural-foreign --natural-primary --indent=4 > testdata.json
    """

    for number in range(1, 100):
        user = User.objects.create_user(username=str(number), password=str(number))
        user.save()

        auction = Auction()
        auction.id = number
        auction.title = u"User {} item".format(user.username)
        auction.description = auction.title
        auction.minimum_bid = 5.0
        auction.expires = datetime.datetime(year=2016, month=12, day=24, hour=13, minute=00, tzinfo=pytz.utc)
        auction.creator_username = user.username
        auction.created = datetime.datetime.now()
        auction.save()

    for number in range(1, 99, 7):
        print number
        auction = Auction.get_by_id(number)
        auction.current_bid = 10.0
        auction.current_bid_timestamp = datetime.datetime.now()
        auction.current_bidder_username = User.objects.get(username=str((number % 6) + 1)).username
        auction.save()

    superuser = User.objects.create_superuser(username="admin", email="hubbe128@gmail.com", password="secureadminpassword")
    superuser.save()

if __name__ == "__main__":
    populate()
