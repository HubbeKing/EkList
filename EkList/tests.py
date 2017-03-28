import os
import datetime
import pytz
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase, Client


class CreateAuction(TestCase):
    fixtures = [os.path.join("EkList", "fixtures", "testdata.json")]

    def test_proper_create(self):
        self.user = User.objects.create_user(username="TestCaseUser", password="1234")
        title = u"Unittest Test Item"
        description = u"A test auction."
        minimum_bid = 5.0
        expires = datetime.datetime(year=2016, month=12, day=24, hour=13, minute=00, tzinfo=pytz.utc).strftime("%Y-%m-%dT%H:%M")

        self.client.get(reverse("home"))
        self.client.get(reverse("create"))

        login_success = self.client.login(username="TestCaseUser", password="1234")
        self.assertTrue(login_success)

        response = self.client.post(reverse("verify"), {"title": title,
                                                        "description": description,
                                                        "minimum_bid": minimum_bid,
                                                        "expires": expires})

        self.assertTemplateUsed(response, "verify_auction.html")
        self.assertContains(response, u"Unittest Test Item")
        self.assertContains(response, u"A test auction.")
        self.assertContains(response, 5.0)
        self.assertContains(response, u"2016")

        response = self.client.post(reverse("create"), {"title": title,
                                                        "description": description,
                                                        "minimum_bid": minimum_bid,
                                                        "expires": expires})
        self.assertEqual(response.status_code, 302)  # this indicates a redirect to the view_auction page

        response = self.client.post(reverse("search"), {"search_term": "Unittest"})

        self.assertContains(response, "Unittest Test Item")
        # this indicates the auction was created and can now be found

    def test_improper_create(self):
        self.user = User.objects.create_user(username="TestCaseUser", password="1234")
        title = u"Unittest Test Item"
        description = u"A test auction."
        minimum_bid = 5.0
        expires = datetime.datetime(year=2016, month=01, day=01, hour=13, minute=00, tzinfo=pytz.utc).strftime("%Y-%m-%dT%H:%M")

        self.client.get(reverse("home"))
        self.client.get(reverse("create"))

        login_success = self.client.login(username="TestCaseUser", password="1234")
        self.assertTrue(login_success)

        response = self.client.post(reverse("verify"), {"title": title,
                                                        "description": description,
                                                        "minimum_bid": minimum_bid,
                                                        "expires": expires})

        self.assertTemplateUsed(response, "create_auction.html")  # this indicates that we gave incorrect data, and were directed back to the create form

        response = self.client.post(reverse("search"), {"search_term": "Unittest"})

        self.assertNotContains(response, "Unittest Test Item")  # The auction was not created and can thus not be found


class BidOnAuction(TestCase):
    fixtures = [os.path.join("EkList", "fixtures", "testdata.json")]

    def test_correct_bid(self):
        self.user = User.objects.create_user(username="TestCaseUser", password="1234")

        client = Client()

        client.get(reverse("home"))
        login_success = client.login(username="TestCaseUser", password="1234")
        self.assertTrue(login_success)

        response = client.get(reverse("auction", kwargs={"auction_id": 10}))
        self.assertTemplateUsed(response, "auction.html")
        self.assertContains(response, "User 10 item")

        response = client.post(reverse("bid", kwargs={"auction_id": 10}), {"description": "User 10 item", "bid_amount": 50.0}, follow=True)
        self.assertRedirects(response, reverse("auction", kwargs={"auction_id": 10}))
        self.assertTemplateUsed(response, "auction.html")
        self.assertContains(response, "Current bid: 50")  # The bid was posted successfully, and is now the current bid.

    def test_too_small_bid(self):
        self.user = User.objects.create_user(username="TestCaseUser", password="1234")

        client = Client()

        client.get(reverse("home"))
        login_success = client.login(username="TestCaseUser", password="1234")
        self.assertTrue(login_success)

        response = client.get(reverse("auction", kwargs={"auction_id": 10}))
        self.assertTemplateUsed(response, "auction.html")
        self.assertContains(response, "User 10 item")

        response = client.post(reverse("bid", kwargs={"auction_id": 10}),
                               {"description": "User 10 item", "bid_amount": 2.0}, follow=True)
        self.assertRedirects(response, reverse("auction", kwargs={"auction_id": 10}))
        self.assertTemplateUsed(response, "auction.html")
        self.assertContains(response, "Given bid is too low. The minimum bid for this auction is 5.0")


class ConcurrentUsers(TestCase):
    fixtures = [os.path.join("EkList", "fixtures", "testdata.json")]

    def test_outbid_while_bidding(self):
        """
        In this test, it is assumed that two users are viewing the same auction at the same time.
        User 1 then bids 25, while User 2 is still thinking.
        User 2 then tries to bid 15, and is rejected, as User 1 has already bid higher.
        """
        self.user1 = User.objects.create_user(username="TestCaseUser1", password="1234")
        self.user2 = User.objects.create_user(username="TestCaseUser2", password="1234")
        client1 = Client()
        client2 = Client()

        client1.get(reverse("home"))
        login_success = client1.login(username="TestCaseUser1", password="1234")
        self.assertTrue(login_success)

        client2.get(reverse("home"))
        login_success = client2.login(username="TestCaseUser2", password="1234")
        self.assertTrue(login_success)

        response = client1.get(reverse("auction", kwargs={"auction_id": 10}))
        self.assertTemplateUsed(response, "auction.html")
        self.assertContains(response, "User 10 item")

        response = client2.get(reverse("auction", kwargs={"auction_id": 10}))
        self.assertTemplateUsed(response, "auction.html")
        self.assertContains(response, "User 10 item")

        response = client1.post(reverse("bid", kwargs={"auction_id": 10}),
                                {"description": "User 10 item", "bid_amount": 25.0}, follow=True)
        self.assertRedirects(response, reverse("auction", kwargs={"auction_id": 10}))
        self.assertTemplateUsed(response, "auction.html")
        self.assertContains(response, "Current bid: 25")

        response = client2.post(reverse("bid", kwargs={"auction_id": 10}),
                                {"description": "User 10 item", "bid_amount": 15.0}, follow=True)
        self.assertRedirects(response, reverse("auction", kwargs={"auction_id": 10}))
        self.assertTemplateUsed(response, "auction.html")
        self.assertContains(response, "You must bid at least 0.01 more than the previous bidder.")
        self.assertContains(response, "Current bid: 25")

    def test_auction_edited_while_bidding(self):
        """
        In this test, it is assumed that the seller edits the auction description while a user is viewing the auction.
        The user then tries to bid, and is rejected, as the description has changed.
        Only after having been shown the new description is the user allowed to bid again.
        """
        self.user = User.objects.create_user(username="TestCaseUser", password="1234")

        client1 = Client()

        client1.get(reverse("home"))
        login_success = client1.login(username="TestCaseUser", password="1234")
        self.assertTrue(login_success)

        response = client1.get(reverse("auction", kwargs={"auction_id": 10}))
        self.assertTemplateUsed(response, "auction.html")
        self.assertContains(response, "User 10 item")

        client2 = Client()

        client2.get(reverse("home"))
        login_success = client2.login(username="10", password="10")
        self.assertTrue(login_success)

        response = client2.get(reverse("auction", kwargs={"auction_id": 10}))
        self.assertTemplateUsed(response, "auction.html")
        self.assertContains(response, "User 10 item")

        response = client2.get(reverse("edit", kwargs={"auction_id": 10}))
        self.assertTemplateUsed(response, "edit_auction.html")

        response = client2.post(reverse("edit", kwargs={"auction_id": 10}), {"description": "New description for item 10"}, follow=True)
        self.assertTemplateUsed(response, "auction.html")
        self.assertContains(response, "New description for item 10")

        response = client1.post(reverse("bid", kwargs={"auction_id": 10}),
                                {"description": "User 10 item", "bid_amount": 25.0}, follow=True)
        self.assertTemplateUsed(response, "auction.html")
        self.assertContains(response, "description was updated, please re-read it before bidding!")

        response = client1.post(reverse("bid", kwargs={"auction_id": 10}),
                                {"description": "New description for item 10", "bid_amount": 25.0}, follow=True)
        self.assertRedirects(response, reverse("auction", kwargs={"auction_id": 10}))
        self.assertTemplateUsed(response, "auction.html")
        self.assertContains(response, "Current bid: 25")  # The bid was now posted successfully, and is the current bid.
