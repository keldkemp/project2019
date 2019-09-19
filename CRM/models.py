from django.db import models
from itertools import count
from django.contrib.auth import get_user_model
from transliterate import translit
from django.contrib.auth.models import AbstractUser, UserManager
from django.urls import reverse, reverse_lazy
from django.utils import timezone

