from django import forms

from events.models import Event, Review


class EventUpdateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('title', 'is_private', 'logo')


class EventDetailForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rate', 'text')


class EventCreationForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'

    date_start = forms.DateTimeField(label='Дата начала',
                                     widget=forms.DateTimeInput(format="%Y-%m-%dT%H:%M",
                                                                attrs={'type': 'datetime-local'})
                                     )

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')

        if Event.objects.filter(title=title).exists():
            raise forms.ValidationError(f'Событие с таким названием {title} уже существует')

        return cleaned_data


class EventCreateUpdateForm(forms.ModelForm):
    date_start = forms.DateTimeField(label='Дата начала',
                                     widget=forms.DateTimeInput(format="%Y-%m-%dT%H:%M",
                                                                attrs={'type': 'datetime-local'})
                                     )

    class Meta:
        model = Event
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_start'].widget.attrs.update({'class': 'form-control'})
