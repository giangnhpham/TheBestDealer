from datetime import datetime
import re
from unicodedata import name
from django.db import models
from django.utils.timezone import now


# Create your models here.
class CarMake(models.Model):
    # - Name
    name = models.CharField(null=False, max_length=50,
                            verbose_name='Name', default='undefined')
    # - Description
    description = models.TextField(blank=True, verbose_name='Description')

    # - __str__ method to print a car make object
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = 'Car Make'


class CarModel(models.Model):
    # - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    # - Name
    name = models.CharField(null=False, max_length=40,
                            default='undefined', verbose_name='Name')
    # - Dealer id, used to refer a dealer created in cloudant database
    dealer_id = models.IntegerField(default=1, verbose_name='Dealer ID')

    # - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
    SEDAN = 'Sedan'
    SUV = 'SUV'
    WAGON = 'Wagon'
    COUPE = 'Coupe'
    SPORTS = 'Sports'
    HATCHBACK = 'Hatchback'
    CONVERTIBLE = 'Convertible'
    MINVAN = 'Minivan'
    TYPE_CHOICES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (WAGON, 'Wagon'),
        (COUPE, 'Coupe'),
        (SPORTS, 'Sports'),
        (HATCHBACK, 'Hatchback'),
        (CONVERTIBLE, 'Convertible'),
        (MINVAN, 'Minivan')
    ]
    type = models.CharField(null=False, max_length=20,
                            choices=TYPE_CHOICES, default=SEDAN, verbose_name='Body Type')

    YEAR_CHOICES = [(year, year) for year in range(1900, datetime.now().year + 2)]
    # - Year (DateField)
    year = models.IntegerField(choices=YEAR_CHOICES, default=1900)

    # - __str__ method to print a car make object
    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Car Model'


class CarDealer:

    def __init__(self, address, city, full_name, id, lat, long, short_name, st, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer Full Name
        self.full_name = full_name
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state
        self.st = st
        # Dealer zip
        self.zip = zip

    def __str__(self):
        return "Dealer name: " + self.full_name

class DealerReview:
    def __init__(self, dealership, name, purchase, review, purchase_date=None, car_make=None, car_model=None, car_year=None, sentiment=None, id=1) -> None:
        self.dealership = dealership
        self.name = name
        self.purchase = purchase
        self.review = review
        self.purchase_date = purchase_date
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.sentiment = sentiment
        self.id = id
    
    def __str__(self) -> str:
        return self.review