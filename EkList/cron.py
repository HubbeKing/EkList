from django_cron import CronJobBase, Schedule
from models import Auction
from django.contrib.auth.models import User


class AuctionResolver(CronJobBase):
    RUN_EVERY_MINS = 5

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "eklist.cron.auction_resolver"

    def do(self):
        print "Resolving auctions..."
        expired_auctions = Auction.get_all_expired()
        for auction in expired_auctions:
            if auction.is_banned:
                continue
            if auction.current_bidder_username != "":
                print "Resolving auction '{}'".format(auction.title)
                seller = User.objects.get(username=auction.creator_username)
                winner = User.objects.get(username=auction.current_bidder_username)
                seller_subject = "EkList - Your auction '{}' has been won by user {}".format(auction.title, auction.current_bidder_username)
                seller_body = "Congratulations!\n\nYour auction has been won by user {}, with a high bid of {}.\n" \
                              "They will contact you from {} to arrange shipping.".format(auction.current_bidder_username,
                                                                                          auction.current_bid,
                                                                                          winner.email)

                winner_subject = "EkList - You have won auction '{}'!".format(auction.title)
                winner_body = "Congratulations!\n\nYou have won auction '{}' with your bid of {}.\n" \
                              "Please contact the seller from this email on {} to arrange shipping.".format(auction.title,
                                                                                                            auction.current_bid,
                                                                                                            seller.email)
                loser_subject = "EkList - Auction '{}' is now over.".format(auction.title)
                loser_body = "We're sorry, the auction '{}' that you bid on was won by someone else.".format(auction.title)

                losers = []
                for bidder in [bidder for bidder in auction.bidders.all()]:
                    if bidder.username != auction.current_bidder_username:
                        losers.append(bidder)
                for loser in losers:
                    loser.email_user(loser_subject, loser_body)
                seller.email_user(seller_subject, seller_body)
                winner.email_user(winner_subject, winner_body)

            else:
                seller = User.objects.get(username=auction.creator_username)
                seller.email_user("EkList - Your auction '{}' ended with no bids.".format(auction.title),
                                  "We're sorry, your auction '{}' was not bid on by any of our users, and has now expired.".format(auction.title))