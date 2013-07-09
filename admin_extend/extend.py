from django import forms
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured


def registered_modeladmin(model_cls):
    try:
        model_admin_cls = type(admin.site._registry[model_cls])
        model_admin_cls._model_cls = model_cls
        return model_admin_cls
    except KeyError:
        raise ImproperlyConfigured(
            "A ModelAdmin for %s needs to already be registered" % model_cls)


def registered_form(model_cls):
    admin_cls = registered_modeladmin(model_cls)
    form_cls = admin_cls.form
    form_cls._admin_cls = admin_cls
    return form_cls


def add_bidirectional_m2m(form_cls):

    class BidirectionalM2MForm(form_cls):

        def _get_bidirectinal_m2m_fields(self):
            try:
                return super(BidirectionalM2MForm, self)._get_bidirectinal_m2m_fields()
            except AttributeError:
                return []

        def _get_m2m_attr_name(self, m2m_field):
            return '%s_set' % m2m_field

        def __init__(self, *args, **kwargs):
            super(BidirectionalM2MForm, self).__init__(*args, **kwargs)
            if self.instance.pk is not None:
                for m2m_field in self._get_bidirectinal_m2m_fields():
                    self.fields[m2m_field].initial = getattr(
                        self.instance, self._get_m2m_attr_name(m2m_field)).all()

        def save(self, commit=True):
            instance = super(BidirectionalM2MForm, self).save(commit=False)
            force_save = self.instance.pk is None
            if force_save:
                instance.save()
            for m2m_field in self._get_bidirectinal_m2m_fields():
                attr_name = '%s_set' % m2m_field
                setattr(self.instance, attr_name, self.cleaned_data[m2m_field])
            if commit:
                if not force_save:
                    instance.save()
                self.save_m2m()
            return instance

    return BidirectionalM2MForm


def extend_registered(extended_cls):
    if issubclass(extended_cls, admin.ModelAdmin):
        admin_cls = extended_cls
        admin.site.unregister(admin_cls._model_cls)
        admin.site.register(admin_cls._model_cls, admin_cls)
        return admin_cls
    elif issubclass(extended_cls, (forms.Form, forms.ModelForm)):
        form_cls = extended_cls
        admin_cls = form_cls._admin_cls
        admin.site.unregister(admin_cls._model_cls)
        admin_cls.form = form_cls
        admin.site.register(admin_cls._model_cls, admin_cls)
        return form_cls
    else:
        raise ValueError("Extended class needs to be a ModelAdmin or Form")
