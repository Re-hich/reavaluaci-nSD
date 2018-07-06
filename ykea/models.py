from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Item(models.Model):
    CATEGORIES = (
        ("beds", "Beds & mattressess"),
        ("furn", "Furniture, wardrobes & shelves"),
        ("sofa", "Sofas & armchairs"),
        ("table", "Tables & chairs"),
        ("texti","Textiles"),
        ("deco","Decoration & mirrors"),
        ("light","Lighting"),
        ("cook","Cookware"),
        ("tablw","Tableware"),
        ("taps","Taps & sinks"),
        ("org", "Organisers & storage accesories"),
        ("toys","Toys"),
        ("leis","Leisure"),
        ("safe","safety"),
        ("diy", "Do-it-yourself"),
        ("floor","Flooring"),
        ("plant","Plants & gardering"),
        ("food","Food & beverages")
    )
    item_number = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_new = models.BooleanField()
    size = models.CharField(max_length=40)
    instructions = models.TextField()
    featured_photo = models.ImageField()
    category = models.CharField(max_length=5, choices=CATEGORIES)
    def __str__(self):
        return  ('[**NEW**]' if self.is_new else '') + "[" + self.category + "] [" + self.item_number + "] " + self.name + " - " + self.description + " (" + self.size + ") : " + str(self.price) + " €"

class ShoppingCart(models.Model):
    item = models.ForeignKey(Item)
    user = models.ForeignKey(User)
    name = models.CharField(max_length=20, default='name')
    bought = models.IntegerField(default=0)
    def __str__(self):
        return "["+self.item.item_number+"] " + self.user.username

#Usuario para poder tener el dinero
class WebUser(models.Model):
    user = models.OneToOneField(User)
    money = models.FloatField(default=1000,null=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User, dispatch_uid="add_webUser")
def add_webUser(sender, instance, **kwargs):
    us = instance
    try:
        profile = WebUser.objects.get(user=us)
    except WebUser.DoesNotExist:
        profile = WebUser.objects.create(user=us, money=1000)
        profile.save()
