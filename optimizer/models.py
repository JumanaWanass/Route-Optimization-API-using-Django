from django.db import models

class FuelPrice(models.Model):
    opis_truckstop_id = models.CharField(max_length=100)
    truckstop_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    rack_id = models.CharField(max_length=100)
    retail_price = models.FloatField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.truckstop_name}, {self.city}, {self.state}: ${self.retail_price}/gallon"