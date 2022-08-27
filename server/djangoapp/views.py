from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect

from .models import CarModel
from .restapis import get_dealer_reviews_from_cf, get_dealers_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json


# Get an instance of a logger
logger = logging.getLogger(__name__)

# CLODANT URL CONSTANT
BASE_URL = "https://31a1c2dd.us-south.apigw.appdomain.cloud/api"

# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request


def login_request(request):
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        print(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        # Try to check if provided credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page
            context = {'message': 'Invalid username and/or password'}
            return render(request, 'djangoapp/login.html', context)
    return render(request, "djangoapp/login.html")

# Create a `logout_request` view to handle sign out request


def logout_request(request):
    print("Log out the user `{}`".format(request.user.username))
    logout(request)
    return redirect('djangoapp:index')


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    if request.method == 'POST':
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        username = request.POST['username']
        password = request.POST['password']
        user_exist = False
        try:
            # Check if username already exist
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create(
                username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context = {'message': 'Username already exists.'}
            return render(request, 'djangoapp/registration.html', context)
    return render(request, 'djangoapp/registration.html')

# Update the `get_dealerships` view to render the index page with a list of dealerships


def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "{}/dealership".format(BASE_URL)
        dealerships = get_dealers_from_cf(url, id=1)
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # return render(request, 'djangoapp/index.html', context)
        return HttpResponse(dealer_names)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    # if request.method == 'GET':
    url = '{}/review'.format(BASE_URL)
    reviews = get_dealer_reviews_from_cf(url, dealer_id=dealer_id)
    print(reviews)
    sentiments = ' '.join([review.sentiment for review in reviews])
    return HttpResponse(sentiments)

# Create a `add_review` view to submit a review


def add_review(request, dealer_id):
    context = {}
    user = request.user
    print(request.POST)
    if request.method == 'POST':
        if user.is_authenticated:
            username = user.username
            payload = dict()
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            review_url = "{}/review".format(BASE_URL)
            reviews = get_dealer_reviews_from_cf(review_url, dealer_id=dealer_id)
            max_id = max([review.id for review in reviews], default=1000)
            payload['id'] = max_id + 1 if max_id >= 1000 else max_id + 1000
            payload['name'] = user.username
            payload['dealership'] = dealer_id
            payload['review'] = request.POST['comment']
            payload['purchase'] = False
            new_payload = {}
            new_payload['review'] = payload
            response = post_request(review_url, payload=new_payload, dealer_id=dealer_id)
            return HttpResponse(response)
        else:
            return HttpResponse("Not authenticated")
    return HttpResponse("GET request")
