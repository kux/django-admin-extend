from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured


def get_registered_modeladmin(model_cls):
    try:
        model_admin_cls = type(admin.site._registry[model_cls])
        model_admin_cls._model_cls = model_cls
        return model_admin_cls
    except KeyError:
        raise ImproperlyConfigured(
            "A ModelAdmin for %s needs to already be registered" % model_cls)


def get_registered_modeladmin_form(model):
    return get_registered_modeladmin(model).form


def extend_registered(admin_cls):
    admin.site.unregister(admin_cls._model_cls)
    admin.site.register(admin_cls._model_cls, admin_cls)
    return admin_cls
