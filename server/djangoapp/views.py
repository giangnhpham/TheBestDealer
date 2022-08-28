from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect

from .models import CarModel
from .restapis import get_dealer_by_id_from_cf, get_dealer_reviews_from_cf, get_dealers_from_cf, post_request
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
        dealerships = get_dealers_from_cf(url)
        context['dealership_list'] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    # if request.method == 'GET':
    dealer_url = '{}/dealership'.format(BASE_URL)
    review_url = '{}/review'.format(BASE_URL)
    dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id)
    if dealer is not None:
        reviews = get_dealer_reviews_from_cf(review_url, dealer_id=dealer_id)
        context['dealer'] = dealer
        context['review_list'] = reviews
    else:
        context['message'] = 'Sorry, The dealer do not exists!!!'
    return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    user = request.user
    dealer_url = '{}/dealership'.format(BASE_URL)
    dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id)
    context['dealer'] = dealer
    if request.method == 'POST':
        if user.is_authenticated:
            username = user.username
            payload = dict()
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            review_url = "{}/review".format(BASE_URL)
            reviews = get_dealer_reviews_from_cf(
                review_url, dealer_id=dealer_id)
            max_id = max([review.id for review in reviews], default=1000)
            payload['id'] = max_id + 1 if max_id >= 1000 else max_id + 1000
            payload['time'] = datetime.utcnow().isoformat()
            payload['name'] = username
            payload['dealership'] = dealer_id
            payload['review'] = request.POST['comment']
            payload['purchase'] = False
            if "purchasecheck" in request.POST:
                if request.POST['purchasecheck'] == 'on':
                    payload['purchase'] = True
                    payload['purchasedate'] = request.POST['purchasedate']
                    payload['car_make'] = car.make.name
                    payload['car_model'] = car.name
                    payload['car_year'] = car.year
            new_payload = {}
            new_payload['review'] = payload
            post_request(review_url, payload=new_payload, dealer_id=dealer_id)
            return redirect('djangoapp:dealer_details', dealer_id=dealer_id)
        else:
            return redirect("djangoapp:login")

    # Get cars for dealer
    cars = CarModel.objects.filter(dealer_id=dealer_id)
    context['cars'] = cars
    return render(request, 'djangoapp/add_review.html', context)
