from django.contrib import admin

from .models import CarMake, CarModel


# Register your models here.

# CarModelInline class
class CarModelInline(admin.StackedInline):
  model = CarModel
  extra = 4

# CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
  list_display = ['name', 'make', 'year', 'type']

# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
  list_display = ['name', 'description']
  inlines = [CarModelInline]

# Register models here
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)