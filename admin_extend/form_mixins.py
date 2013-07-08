from django.forms import ModelForm


class BidirectionalM2MForm(ModelForm):

    bi_m2m_fields = []

    def _get_m2m_attr_name(self, m2m_field):
        return '%s_set' % m2m_field

    def __init__(self, *args, **kwargs):
        super(BidirectionalM2MForm, self).__init__(*args, **kwargs)
        if self.instance.pk is not None:
            for m2m_field in self.bi_m2m_fields:
                self.fields[m2m_field].initial = getattr(
                    self.instance, self._get_m2m_attr_name(m2m_field)).all()

    def save(self, commit=True):
        instance = super(BidirectionalM2MForm, self).save(commit=False)
        force_save = self.instance.pk is None
        if force_save:
            instance.save()
        for m2m_field in self.bi_m2m_fields:
            attr_name = '%s_set' % m2m_field
            setattr(self.instance, attr_name, self.cleaned_data[m2m_field])
        if commit:
            if not force_save:
                instance.save()
            self.save_m2m()
        return instance
