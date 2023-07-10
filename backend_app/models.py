from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.gis.db import models
from django.contrib.gis.geos import LineString

# Create your models here.


class CustomUserManager(models.Manager):
    """Custom manager that only returns users from Nepal"""

    def get_queryset(self):
        return super().get_queryset().filter(country='Nepal')


class User(AbstractUser):
    country = models.CharField(max_length=100, null=True)
    bio = models.TextField(null=True)
    phone_number = models.CharField(max_length=10, null=True)
    areas_of_interest = models.ManyToManyField('Interest', blank=True)
    documents = models.FileField(
        upload_to='user_documents/', blank=True, null=True)
    birthday = models.DateField(null=True)
    home_address = models.PointField(geography=True, null=True)
    office_address = models.PointField(geography=True, null=True)

    REQUIRED_FIELDS = ['email', 'country']

    objects = UserManager()
    nepali = CustomUserManager()

    # Model method that returns distance between home and office in km
    def get_home_office_distance(self):
        if self.home_address and self.office_address:
            distance = self.home_address.distance(self.office_address)
            distance_in_km = distance * 100
            return round(distance_in_km, 2)

    @property
    def age(self):
        from datetime import date
        today = date.today()
        age = today.year - self.birthday.year
        if today < date(today.year, self.birthday.month, self.birthday.day):
            age -= 1
        return age

    def __str__(self):
        return self.username


class Interest(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class UserLine(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    line = models.LineStringField(geography=True, null=True, blank=True)

    def construct_line(self):
        home = self.user.home_address
        office = self.user.office_address
        if home and office:
            line = LineString(home, office)
            self.line = line

    def save(self, *args, **kwargs):
        self.construct_line()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Line from {self.user.username}'s home to office"
