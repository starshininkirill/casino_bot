from django.db import models


class User(models.Model):
    username = models.CharField(max_length=100, null=True)
    tg_uid = models.IntegerField()
    balance = models.IntegerField(default=0)
    stage = models.CharField(max_length=50, default='menu')
    games_count = models.IntegerField(default=0)


class Stages(models.Model):
    current_stage = models.CharField(max_length=50, null=True)
    next_stage = models.CharField(max_length=50, null=True)


class CubeGame(models.Model):
    tg_uid = models.IntegerField(null=True)
    bet = models.IntegerField(null=True)
    position = models.IntegerField(null=True)
