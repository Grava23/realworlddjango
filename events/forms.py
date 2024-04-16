from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.forms import PasswordResetForm
from events.models import Event, Review, Enroll
from .models import CustomUser, User
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError


class EventUpdateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('title', 'is_private', 'logo')


# class EventDetailForm(forms.ModelForm):
#     rate = forms.IntegerField(label='Оценка', min_value=1, max_value=5)
#     text = forms.CharField(label='Текст отзыва', widget=forms.Textarea)
#     event = forms.IntegerField(widget=forms.HiddenInput())
#
#     class Meta:
#         model = Review
#         fields = ['rate', 'text', 'event']


class EnrollForm(forms.ModelForm):
    class Meta:
        model = Enroll
        fields = []


class ReviewForm(forms.ModelForm):
    RATE_CHOICES = (
        (1, '1 звезда'),
        (2, '2 звезды'),
        (3, '3 звезды'),
        (4, '4 звезды'),
        (5, '5 звезд'),
    )

    rate = forms.ChoiceField(choices=RATE_CHOICES, label='Оценка')

    class Meta:
        model = Review
        fields = ['rate', 'text']  # Обновляем список полей для формы
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }


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


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(label='Username', max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    email = forms.EmailField(label='Email')

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email']


class MailForm(forms.Form):
    subject = forms.CharField(label='Тема')
    message = forms.CharField(label='Сообщение', widget=forms.Textarea)


class CustomPasswordChangeForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают")


class CustomPasswordResetForm(PasswordResetForm):
    pass


class SubscriberForm(forms.Form):
    subscriber_email = forms.EmailField(label='Email подписчика', required=True)


class LetterForm(forms.Form):
    subject = forms.CharField(label='Тема письма', max_length=100, required=True)
    message = forms.CharField(label='Текст письма', widget=forms.Textarea, required=True)


class AvatarForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['avatar']


class UsernameForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username']


class EmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'username']
        widgets = {
            'username': forms.HiddenInput(),
        }