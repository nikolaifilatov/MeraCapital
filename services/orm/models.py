from django.db import models


class Account(models.Model):
    account_id = models.CharField(primary_key=True, max_length=64)


class Calculation(models.Model):
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    btc_rate = models.DecimalField(decimal_places=10, max_digits=20)
    net_assets = models.DecimalField(decimal_places=10, max_digits=20)
    pnl = models.DecimalField(decimal_places=10, max_digits=20)
    pnl_index = models.DecimalField(decimal_places=10, max_digits=20)
