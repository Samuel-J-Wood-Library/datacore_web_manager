# Use datetime if not localizing timezones
import datetime
# Otherwise use timezone
from django.utils import timezone 
from django.contrib.humanize.templatetags.humanize import intcomma

from django import template

register = template.Library()

@register.filter
def hours_ago(time, hours):
    return time + datetime.timedelta(hours=hours) < datetime.datetime.now() # or timezone.now() if your time is offset-aware

@register.filter
def days_ago(date, days):
    return date + datetime.timedelta(days=days) < datetime.date.today() 

@register.filter
def days_until(date, days):
    return date - datetime.date.today() < datetime.timedelta(days=days)
    
 
 
@register.filter
def account_format(dollar):
    if dollar:
        return "${:>10,.2f}".format(dollar)
    else:
        return "${:>10,.2f}".format(0.00)