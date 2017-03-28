import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from models import Auction, UserData


def home_page(request):
    """
    Show home page with list of all valid auctions - "Browsing"
    """
    if "preferred_language" not in request.session or not request.session["preferred_language"]:
        session_init(request)
    auctions = Auction.get_all_valid()
    paginator = Paginator(auctions, 10)
    page = request.GET.get("page")
    try:
        auctions = paginator.page(page)
    except PageNotAnInteger:
        auctions = paginator.page(1)
    except EmptyPage:
        auctions = paginator.page(paginator.num_pages)
    return render(request, "home.html",
                  {"auctions": auctions,
                   "language": request.session["preferred_language"]})


def view_auction(request, auction_id):
    """
    Show data for a single auction
    """
    if "preferred_language" not in request.session or not request.session["preferred_language"]:
        session_init(request)
    if Auction.exists(auction_id):
        auction = Auction.get_by_id(auction_id)
        return render(request, "auction.html",
                      {"auction": auction,
                       "time_remaining": Auction.get_time_remaining(auction.id),
                       "language": request.session["preferred_language"]})
    else:
        return HttpResponseRedirect(reverse("home"))


def search_auction(request):
    """
    Search the auction "database"
    """
    if "preferred_language" not in request.session or not request.session["preferred_language"]:
        session_init(request)
    if request.method == "POST":
        search_term = request.POST.get("search_term")
    else:
        search_term = request.GET.get("search_term")
    title_results = Auction.objects.filter(title__contains=search_term)
    search_results = title_results
    paginator = Paginator(search_results, 10)
    page = request.GET.get("page")
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)
    return render(request, "home.html",
                  {"auctions": search_results,
                   "search_term": search_term,
                   "language": request.session["preferred_language"]})


@login_required
def post_bid(request, auction_id):
    if "preferred_language" not in request.session or not request.session["preferred_language"]:
        session_init(request)
    if request.method == "POST":
        if Auction.get_by_id(auction_id).description != request.POST.get("description"):
            # This should ensure the user has always been shown the latest description before accepting a bid.
            messages.error(request, "The auction's description was updated, please re-read it before bidding!")
            return HttpResponseRedirect(reverse("auction", kwargs={"auction_id": auction_id}))
        # This is the DUMBEST thing, but it should get around the floating point presentation problem
        # In case a user bids 10.0000000000001 or something similar in an attempt to break things.
        bid_amount = float(format(float(request.POST.get("bid_amount")), u".2f"))
        current_bidder = Auction.get_by_id(auction_id).current_bidder_username
        new_bidder = request.user.username
        creator = Auction.get_by_id(auction_id).creator_username
        if Auction.get_by_id(auction_id).is_banned:
            messages.error(request, "We are sorry, this auction has been banned by our administrators.")
            return HttpResponseRedirect(reverse("auction", kwargs={"auction_id": auction_id}))
        elif new_bidder == creator:
            messages.error(request, "You cannot bid on your own auctions.")
            return HttpResponseRedirect(reverse("auction", kwargs={"auction_id": auction_id}))
        elif current_bidder == new_bidder:
            messages.error(request, "There is no need to outbid yourself.")
            return HttpResponseRedirect(reverse("auction", kwargs={"auction_id": auction_id}))
        elif Auction.is_expired(auction_id):
            messages.error(request, "We're sorry, this auction has already expired.")
            return HttpResponseRedirect(reverse("auction", kwargs={"auction_id": auction_id}))
        elif bid_amount <= Auction.get_by_id(auction_id).minimum_bid:
            messages.error(request, "Given bid is too low. The minimum bid for this auction is {}".format(
                Auction.get_by_id(auction_id).minimum_bid))
            return HttpResponseRedirect(reverse("auction", kwargs={"auction_id": auction_id}))
        elif Auction.has_bid(auction_id) and bid_amount <= Auction.get_by_id(auction_id).current_bid:
            # This should handle concurrent bids
            # Unless two bids happen at the exact same millisecond and are processed at the exact same speed
            # Which should be reasonably impossible for our purposes.
            messages.error(request, "You must bid at least 0.01 more than the previous bidder.")
            return HttpResponseRedirect(reverse("auction", kwargs={"auction_id": auction_id}))
        else:
            auction = Auction.get_by_id(auction_id)
            tzinfo = auction.expires.tzinfo
            if auction.expires - datetime.datetime.now(tzinfo) < datetime.timedelta(minutes=5):
                # this allows for further bidding at the end of an auction, if multiple parties are interested.
                auction.expires = auction.expires + datetime.timedelta(minutes=5)
            auction.current_bid = bid_amount
            auction.current_bidder_username = new_bidder
            auction.current_bid_timestamp = datetime.datetime.now()
            auction.bidders.add(User.objects.get(username=new_bidder))
            auction.save()

            mail_subject = "EkList - New bid on auction '{}' - {}".format(auction.title, auction.current_bid)
            seller_body = "New high bid on your auction '{}' - {} from user {}!".format(auction.title,
                                                                                        auction.current_bid,
                                                                                        auction.current_bidder_username)

            bidder_body = "Your bid of {} on auction '{}' was registered.".format(auction.current_bid,
                                                                                  auction.title)

            prev_body = "You have been outbid on auction '{}' by user {}!".format(auction.title,
                                                                                  auction.current_bidder_username)
            try:
                User.objects.get(username=auction.creator_username).email_user(mail_subject, seller_body)
                User.objects.get(username=new_bidder).email_user(mail_subject, bidder_body)
            except:
                pass
            if current_bidder is not None and current_bidder != "":
                try:
                    User.objects.get(username=current_bidder).email_user(mail_subject, prev_body)
                except:
                    pass

            messages.success(request, "Bid successfully entered.")
            return HttpResponseRedirect(reverse("auction", kwargs={"auction_id": auction_id}))


@login_required
def create_auction(request):
    if "preferred_language" not in request.session or not request.session["preferred_language"]:
        session_init(request)
    if request.method == "POST":
        auction = Auction()
        auction.title = request.POST.get("title")
        auction.description = request.POST.get("description")
        auction.minimum_bid = float(request.POST.get("minimum_bid"))
        auction.expires = datetime.datetime.strptime(request.POST.get("expires"), "%Y-%m-%dT%H:%M")
        auction.creator_username = request.user.username
        auction.created = datetime.datetime.now()
        auction.save()
        messages.success(request, "Auction created successfully.")
        return HttpResponseRedirect(reverse("auction", kwargs={"auction_id": auction.id}))
    else:
        if "title" in request.GET:
            auction_data = {"title": request.GET.get("title"),
                            "description": request.GET.get("description"),
                            "minimum_bid": request.GET.get("minimum_bid"),
                            "expires": request.GET.get("expires")}
            return render(request, "create_auction.html",
                          {"language": request.session["preferred_language"],
                           "auction": auction_data})
        else:
            return render(request, "create_auction.html",
                          {"language": request.session["preferred_language"]})


@login_required
def verify_auction(request):
    auction_info = {"title": request.POST.get("title"), "description": request.POST.get("description"),
                    "minimum_bid": request.POST.get("minimum_bid"),
                    "expires": request.POST.get("expires")}

    # This shouldn't happen, but if the user's browser doesn't support the "required" html tag, it MAY happen.
    if len(auction_info["title"]) == 0 or len(auction_info["description"]) == 0 or len(
            auction_info["minimum_bid"]) == 0 or not auction_info["expires"]:
        messages.error(request, "Not all fields were filled out, please verify information and try again.")
        return render(request, "create_auction.html",
                      {"language": request.session["preferred_language"],
                       "auction": auction_info})
    elif datetime.datetime.strptime(auction_info["expires"], "%Y-%m-%dT%H:%M") > datetime.datetime.now() and datetime.datetime.strptime(auction_info["expires"], "%Y-%m-%dT%H:%M") - datetime.datetime.now() < datetime.timedelta(hours=72):
        messages.error(request, "Auction expiry date must be at least 72 hours in the future.")
        return render(request, "create_auction.html",
                      {"language": request.session["preferred_language"],
                       "auction": auction_info})

    elif datetime.datetime.strptime(auction_info["expires"], "%Y-%m-%dT%H:%M") < datetime.datetime.now():
        messages.error(request, "Auction expiry date must be at least 72 hours in the future.")
        return render(request, "create_auction.html",
                      {"language": request.session["preferred_language"],
                       "auction": auction_info})
    else:
        return render(request, "verify_auction.html",
                      {"language": request.session["preferred_language"],
                       "auction": auction_info})


@login_required
def edit_auction(request, auction_id):
    if "preferred_language" not in request.session or not request.session["preferred_language"]:
        session_init(request)
    if request.user.username != Auction.get_by_id(auction_id).creator_username:
        return HttpResponseRedirect(reverse("auction", kwargs={"auction_id": auction_id}))

    if request.method == "POST":
        if "description" in request.POST and len(request.POST.get("description")) > 0:
            auction = Auction.get_by_id(auction_id)
            auction.description = request.POST.get("description")
            auction.modified = datetime.datetime.now()
            auction.save()
            messages.success(request, "Auction description was changed successfully.")
            return HttpResponseRedirect(reverse("auction", kwargs={"auction_id": auction_id}))
    else:
        auction = Auction.get_by_id(auction_id)
        return render(request, "edit_auction.html",
                      {"language": request.session["preferred_language"],
                       "auction": auction})


@login_required
@permission_required("EkList.ban_auction")
def ban_auction(request, auction_id):
    """
    Ban an auction from the site
    """
    if "preferred_language" not in request.session or not request.session["preferred_language"]:
        session_init(request)
    if Auction.exists(auction_id):
        auction = Auction.get_by_id(auction_id)
        auction.is_banned = True
        auction.expires = datetime.datetime.now()
        auction.modified = auction.expires
        auction.description += "\nThis auction has been banned by the EkList administrators."
        auction.save()

        email_subject = "Auction '{}' has been banned from EkList.".format(auction.title)
        email_body = "We are sorry, but the auction '{}' does not comply with our terms of service and has thus been banned.".format(
            auction.title)
        try:
            User.objects.get(username=auction.creator_username).email_user(email_subject, email_body)
        except:
            pass
        bidders = [user for user in auction.bidders.all()]
        if len(bidders) > 0:
            for user in bidders:
                user.email_user(email_subject, email_body)

        messages.success(request, "Auction banned successfully.")
        return HttpResponseRedirect(reverse("home"))
    messages.error(request, "Auction with id '{}' not found.".format(auction_id))
    return HttpResponseRedirect(reverse("home"))


def login_user(request):
    """
    Authenticate and login user
    """
    if "preferred_language" not in request.session or not request.session["preferred_language"]:
        session_init(request)
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if UserData.exists(user=username):
                user_data = UserData.get_user_data(user=username)
            else:
                user_data = UserData()
                user_data.username = username
                user_data.preferred_language = "en_US"
                user_data.save()
            request.session["preferred_language"] = user_data.preferred_language
            return HttpResponseRedirect(request.GET.get("next", reverse("home")))
        else:
            messages.error(request, "Username or password not correct.")
            return HttpResponseRedirect(reverse("login"))
    else:
        # GET request
        # display login form
        return render(request, "login_form.html",
                      {"next": request.GET.get("next", reverse("home")),
                       "language": request.session["preferred_language"]})


def register_user(request):
    """
    Show registration form and create new user accounts
    """
    if "preferred_language" not in request.session or not request.session["preferred_language"]:
        session_init(request)
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            user_data = UserData()
            user_data.username = username
            user_data.preferred_language = "en_US"
            user_data.save()
            messages.success(request, "Account created successfully. You may now log in.")
            return HttpResponseRedirect(reverse("home"))
        else:
            messages.error(request, "Account not created. Username already in use.")
            return HttpResponseRedirect(reverse("register"))
    else:
        # GET request
        # display registration form
        return render(request, "registration_form.html",
                      {"language": request.session["preferred_language"]})


@login_required
def user_profile(request, username):
    """
    View & Edit user profile data
    """
    if "preferred_language" not in request.session or not request.session["preferred_language"]:
        session_init(request)
    if request.method == "POST":
        if "email" in request.POST and len(request.POST.get("email")) > 0:
            user = User.objects.get(username=username)
            user.email = request.POST.get("email")
            user.save()
            messages.success(request, "Email address successfully changed.")
            return HttpResponseRedirect(reverse("profile_page", kwargs={"username": username}))
    else:
        user_auctions = Auction.get_by_creator(username=username)
        paginator = Paginator(user_auctions, 10)
        page = request.GET.get("page")
        try:
            user_auctions = paginator.page(page)
        except PageNotAnInteger:
            user_auctions = paginator.page(1)
        except EmptyPage:
            user_auctions = paginator.page(paginator.num_pages)
        return render(request, "profile.html",
                      {"auctions": user_auctions,
                       "language": request.session["preferred_language"],
                       "user": User.objects.get(username=username)})


def logout_session(request):
    logout(request)
    return HttpResponseRedirect(reverse("home"))


def redirect_home(request):
    return HttpResponseRedirect(reverse("home"))


def password_change_done(request):
    messages.success(request, "Password successfully changed.")
    return HttpResponseRedirect(reverse("home"))


def password_reset_done(request):
    messages.success(request, "Password reset has been sent. It may take several minutes to arrive in your inbox.")
    return HttpResponseRedirect(reverse("home"))


def password_reset_complete(request):
    messages.success(request, "Password reset completed successfully. You may now log in.")
    return HttpResponseRedirect(reverse("home"))


def toggle_language(request):
    if request.session["preferred_language"] == "en_US":
        if request.user.is_authenticated:
            user_data = UserData.get_user_data(user=request.user.username)
            user_data.preferred_language = "sv_SE"
            user_data.save()
        request.session["preferred_language"] = "sv_SE"
    else:
        if request.user.is_authenticated:
            user_data = UserData.get_user_data(user=request.user.username)
            user_data.preferred_language = "en_US"
            user_data.save()
        request.session["preferred_language"] = "en_US"
    return HttpResponseRedirect(request.GET.get("next"))


def session_init(request):
    if request.user.is_authenticated:
        if UserData.exists(request.user.username):
            request.session["preferred_language"] = UserData.get_language(user=request.user.username)
        else:
            user_data = UserData()
            user_data.username = request.user.username
            user_data.preferred_language = "en_US"
            user_data.save()
    else:
        request.session["preferred_language"] = "en_US"
