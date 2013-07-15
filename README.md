django-admin-extend
===================
Django app that provides an easy way of extending or overriding behaviour of
ModelAdmin classes that have already been registered by other apps.

This is usually useful when the ```ModelAdmin``` you're altering is part of
a third-party app that you can't/wouldn't want to fork.

Extending model admins
====================================
Let's assume we have a django project which uses ```django.contrib.auth```.

Most of the times you have a many-to-many relation you would like your 
selection field to use [filter_horizontal](https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.filter_horizontal).
However, django.contrib.auth.admin.UserAdmin uses the simple ```<select multiple>``` which
is incredibly annoying to use.

To be able to use ```filter_horizontal``` with ```UserAdmin``` you can use django-admin-extend
in the admin module of one of the apps you write:


```
# admin.py
from django.contrib.auth.models import User


@extend_registered
class ExtendedUserAdmin(registered_modeladmin(User)):
    filter_horizontal = ('user_permissions', 'groups')


```

You can also override a ModelAdmin's ModelForm:

```
# admin.py
from django.core.exceptions import ValidationError


@extend_registered
class ExtendedUserForm(registered_form(User)):

    def clean_username(self):
        username = self.cleaned_data.get('username', None)
        if username and not username.isalpha():
            raise ValidationError('Invalid username. Only alphabetic characters allowed')
        return username

```

The advantage of using ```registered_modeladmin``` over explicitly inheriting from
the ```ModelAdmin``` is the fact that multiple apps can override
functionality and remain decoupled.

**Note**: The order of in the ```INSTALLED_APPS``` setting matters.
The app that uses ```extend_registered``` needs to be **after** the app that first
defines and registers the ```ModelAdmin```.

The alternative would be to use explicit inheritance:

```
# app1.admin
class App1UserAdmin(UserAdmin):
    pass
```

```
# app2.admin
class App2UserAdmin(App1UserAdmin):
    pass
```

But this creates a dependency between ```app2``` and ```app1```.


Bidirectional many to many fields
========================================================

This is a generic mechanism for implementing an old
[feature request](https://code.djangoproject.com/ticket/897) that never
got into django.

Let's assume you're using ```django.contrib.sites``` and one of your models (let's say
```Snippet```) has a many to many relation with the ```Site``` model. Whenever you add
a new site, you want to be able to assign snippets to that new site.

You can do this by using ```add_bidirectional_m2m```:

```
# models.py
class Snippet(models.Model):
    name = models.CharField(unique=True, max_length=255)
    sites = models.ManyToManyField(Site, null=False, blank=True)
```

```
# admin.py
@extend_registered
class ExtendedSiteAdminForm(add_bidirectional_m2m(registered_form(Site))):

    snippets = ModelMultipleChoiceField(
        queryset=Snippet.objects.all(),
        widget=FilteredSelectMultiple()
    )

    def _get_bidirectional_m2m_fields(self):
        return super(ExtendedSiteAdminForm, self).\
            _get_bidirectional_m2m_fields() + [('snippets', 'smartsnippet_set')]

```

```_get_bidirectinal_m2m_fields``` needs to return a list of tuples, where each
tuple contains the form field name and the related manager's name.

Mind the fact that if the object you're saving is new, then the form's ```save```
method will cause a database save regardless of the value of the commit parameter. 


The extension above can also be made from multiple apps, each injecting their own
bidirectional many to many fields.
  
See [bidirectional_many_to_many.png](https://github.com/kux/django-admin-extend/blob/master/bidirectional_many_to_many.png)
for an example of how this would look.
