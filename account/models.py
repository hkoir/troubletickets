
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin,Group,Permission)
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid



class CustomAccountManager(BaseUserManager):

    def create_superuser(self, email, name, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

       
        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, name, password, **other_fields)

    def create_user(self, email, name, password, **other_fields):

        if not email:
            raise ValueError('You must provide an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name,
                          **other_fields)
        user.set_password(password)
        user.save()
        return user


class Customer(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    groups = models.ManyToManyField(
        Group,
        related_name='customer_set',
        blank=True,
        help_text=_("The groups this user belongs to."),
        verbose_name=_("groups"),
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customer_set',
        blank=True,
        help_text=_("Specific permissions for this user."),
        verbose_name=_("user permissions"),
    )

    USER_LEVEL_CHOICES = [
        ('general_user', 'General_User'),
        ('first_level', 'First Level Manager'),
        ('second_level', 'Second Level Manager'),
        ('third_level', 'Third Level Manager'),
        ('external', 'External'),
    ]
    manager_level = models.CharField(max_length=20, choices=USER_LEVEL_CHOICES, default='general_user')

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = "Accounts"
        verbose_name_plural = "Accounts"

    def email_user(self, subject, message):
        send_mail(
            subject,
            message,
            'l@1.com',
            [self.email],
            fail_silently=False,
        )

    def __str__(self):
        return self.name

class Address(models.Model):  
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, verbose_name=_("Customer"), on_delete=models.CASCADE)
    full_name = models.CharField(_("Full Name"), max_length=150)
    phone = models.CharField(_("Phone Number"), max_length=50)
    postcode = models.CharField(_("Postcode"), max_length=50)
    address_line = models.CharField(_("Address Line 1"), max_length=255)
    address_line2 = models.CharField(_("Address Line 2"), max_length=250,blank=True, null=True)
    town_city = models.CharField(_("Town/City/State"), max_length=150)
    delivery_instructions = models.CharField(_("Delivery Instructions"), max_length=255)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    default = models.BooleanField(_("Default"), default=False)  
    

   
    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

    def __str__(self):
        return "Address"
    






    
class AudioModel(models.Model):       
    success_audio = models.FileField(upload_to='audio/', blank=True, null=True)  
    failure_audio = models.FileField(upload_to='audio/', blank=True, null=True)

    welcome_message = models.FileField(upload_to='audio/', blank=True, null=True)  
    account_create_success = models.FileField(upload_to='audio/', blank=True, null=True)
    request_for_logged_in = models.FileField(upload_to='audio/', blank=True, null=True)  
    logged_in_success = models.FileField(upload_to='audio/', blank=True, null=True)
    forget_password = models.FileField(upload_to='audio/', blank=True, null=True)  
    order_placed_success = models.FileField(upload_to='audio/', blank=True, null=True)
    hold_on_message = models.FileField(upload_to='audio/', blank=True, null=True)
    please_login_to_review = models.FileField(upload_to='audio/', blank=True, null=True)
