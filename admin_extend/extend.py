from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured


def get_registered_modeladmin(model):
    try:
        return type(admin.site._registry[model])
    except KeyError:
        raise ImproperlyConfigured(
            "A ModelAdmin for %s needs to already be registered" % model)


def get_registered_modeladmin_form(model):
    return get_registered_modeladmin(model).form


def extend_registered(model_cls):

    def decorator(admin_cls):
        admin.site.unregister(model_cls)
        admin.site.register(model_cls, admin_cls)
        return admin_cls

    return decorator


