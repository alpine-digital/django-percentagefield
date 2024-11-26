# Django Percentage Field

This package add a ``PercentageField`` to Django (also works with Unfold, some minor styling improvements needed) that
shows a percentage in the admin as ``21%``, but stores it as a Decimal - ``0.2100`` - to the database.
This makes it clearer for admins what the field represents, while the decimal value makes actual calculations easier.

## Installation

Run `pip install django-percentagefield` (or `poetry add django-percentagefield`)

## Settings

- add ``django_percentagefield`` to your ``INSTALLED_APPS`` **before** ``django.contrib.admin``
- in your ``models.py``, add the ``PercentageField`` as such:

```python models.py
from django.db import models

from django_percentagefield.db.models import PercentageField


class YourModel(models.Model):
    percentage_field = PercentageField()
```

- in your ``admin.py``, add the following wherever you use ``PercentageField``:

```python admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django_percentagefield.utils import format_percentage

from .models import YourModel


@admin.register(YourModel)
class YourModelAdmin(admin.ModelAdmin):
    list_display = ('formatted_percentage_field',)

    def formatted_percentage_field(self, instance: YourModel) -> str:
        return format_percentage(value=instance.percentage_field, include_percentage_symbol=True)

    formatted_percentage_field.short_description = _('PercentageField description')
```

- _[optional]_: add ``PERCENTAGE_MAX_DIGITS`` and ``PERCENTAGE_DECIMAL_PLACES`` to your ``settings.py`` (default values
  ``7`` and ``4`` respectively)

**TODO**: make the ``django-percentagefield`` package handle the formatting in ``list_display``, ``readonly_fields``,
etc. automatically.