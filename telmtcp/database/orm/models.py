from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class tbl_user(AbstractUser):
    s_password = models.CharField(default='', max_length=512)
    phone = models.CharField(max_length=255, blank=True)
    affiliate = models.IntegerField(blank=True, default=0)
    eth_address = models.CharField(max_length=1024, blank=True)
    eth_private = models.CharField(max_length=1024, blank=True)
    eth_balance = models.FloatField(blank=True, default=0)


class tbl_plan(models.Model):
    name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    price = models.FloatField(blank=True, default=0)
    period = models.CharField(max_length=255, blank=True)
    account_count = models.IntegerField(blank=True, default=0)

class tbl_order(models.Model):
    userid = models.IntegerField(blank=True)
    phone = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    account = models.CharField(max_length=255, blank=True)
    plan_id = models.IntegerField(blank=True, default=0)
    expire_date = models.DateTimeField(blank=True)
    create_date = models.DateTimeField(blank=True)
    subscription_id = models.CharField(max_length=255, blank=True)
    custom_account_cn = models.IntegerField(blank=True, default=0)
    subscription_deactived = models.IntegerField(blank=True, default=0)
    price = models.FloatField(blank=True, default=0)
    custom_plan_type = models.CharField(max_length=255, blank=True)
    affiliate = models.IntegerField(blank=True, default=0)

class tbl_blocked_ip(models.Model):
    blocked = models.CharField(max_length=255, blank=True)

class tbl_custom_plan(models.Model):
    type = models.CharField(max_length=255, blank=True)
    price = models.FloatField(blank=True, default=0)

class tbl_demo(models.Model):
    account = models.CharField(max_length=255, blank=True)
    register_date = models.DateTimeField(blank=True, auto_now_add=True)
    expire_date = models.DateTimeField(blank=True, auto_now_add=True)

class tbl_ip(models.Model):
    account = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=255, blank=True)
    register_date = models.DateTimeField(blank=True, auto_now_add=True)
    ip = models.CharField(max_length=255, blank=True)

class tbl_patch(models.Model):
    version = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=255, blank=True)

class tbl_schema(models.Model):
    type = models.IntegerField(blank=True, default=0)
    expression = models.CharField(max_length=2555, blank=True)

class tbl_alert(models.Model):
    type = models.CharField(max_length=255, blank=True)
    message = models.CharField(max_length=255, blank=True)
    priority = models.CharField(max_length=255, blank=True)
    status = models.IntegerField(blank=True, default=0)


class tbl_crypto_order(models.Model):
    user_id = models.IntegerField(blank=False, default=0)
    crypto = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=1255, blank=True)
    private = models.CharField(max_length=1255, blank=True)
    plan_id = models.IntegerField(blank=True, default=0)
    expire_date = models.DateTimeField(blank=True)
    create_date = models.DateTimeField(blank=True)
    custom_account_cn = models.IntegerField(blank=True, default=0)
    amount = models.FloatField(blank=True, default=0)
    received = models.FloatField(blank=True, default=0)
    price = models.FloatField(blank=True, default=0)
    custom_plan_type = models.CharField(max_length=255, blank=True)
    affiliate = models.IntegerField(blank=True, default=0)
    ex_price = models.FloatField(blank=True, default=0)
    gas_price = models.FloatField(blank=True, default=0)
    status = models.IntegerField(blank=False, default=0)
    order_id = models.CharField(max_length=255, blank=True)
    txs = models.CharField(max_length=1024, blank=True)
    refunded = models.FloatField(blank=True, default=0)
    ref_code = models.IntegerField(blank=True, default=0)
    ref_message = models.CharField(max_length=255, blank=True)
    ref_tx = models.CharField(max_length=255, blank=True)
    transferred = models.IntegerField(blank=True, default=0)


class tbl_promo_email(models.Model):
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField(max_length=10240, blank=True)
    sent = models.IntegerField(blank=True, default=0)
