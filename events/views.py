from django.db.utils import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth import logout
from django.db.models import Avg

from .forms import (EventUpdateForm, EventCreationForm, LoginForm, CustomUserCreationForm, EmailForm,
                    CustomPasswordChangeForm, SubscriberForm, LetterForm, AvatarForm, UsernameForm, MailForm,
                    EnrollForm, ReviewForm)
from .models import (Event, Review, Feature, Enroll, User, Category, Subscriber, CustomUser)


class IndexView(View):
    template_name = 'events/index.html'

    def get(self, request):
        top_rated_reviews = Review.objects.order_by('-rate')[:3]
        top_rated_events = [review.event for review in top_rated_reviews]
        context = {
            'top_rated_events': top_rated_events,
            'top_rated_reviews': top_rated_reviews
        }
        return render(request, self.template_name, context)


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'event'
    paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()  # Добавляем список категорий в контекст
        context['features'] = Feature.objects.all()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        feature_id = self.request.GET.get('feature')
        if feature_id:
            queryset = queryset.filter(feature__id=feature_id)
        category_id = self.request.GET.get('category')  # Получаем значение фильтра из GET-параметров
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        date_start = self.request.GET.get('date_start')
        if date_start:
            queryset = queryset.filter(date_start__date=date_start)
        is_private = self.request.GET.get('is_private')
        if is_private:
            queryset = queryset.filter(is_private=True)
        is_available = self.request.GET.get('is_available')
        if is_available:
            queryset = queryset.filter(available_places__gt=0)
        return queryset.order_by('-pk')


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reviews = self.object.reviews.all()
        context['reviews'] = reviews
        context['rate'] = self.object.rate(reviews)
        context['participants'] = 100 - self.object.participants_number

        if self.object.is_private:
            context['private'] = 'private'
        else:
            context['private'] = 'is_available'

        enroll_form = EnrollForm(initial={'event': self.object})
        context['enroll_form'] = enroll_form

        review_form = ReviewForm()  # Заменяем EventDetailForm на ReviewForm
        context['review_form'] = review_form

        return context

    def post(self, request, *args, **kwargs):
        event = self.get_object()

        if 'enroll' in request.POST:
            enroll_form = EnrollForm(request.POST)
            if enroll_form.is_valid():
                enroll = enroll_form.save(commit=False)
                enroll.event = event
                enroll.user = request.user

                try:
                    enroll.save()
                except IntegrityError:
                    return self.render_to_response(
                        self.get_context_data(form=enroll_form, error='User already registered for this event'))

                return redirect('events:event-detail', pk=event.pk)
            else:
                context = self.get_context_data(form=enroll_form)
                return self.render_to_response(context)

        elif 'review' in request.POST:
            review_form = ReviewForm(request.POST)  # Используем ReviewForm для создания отзыва
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.event = event
                review.user = request.user
                review.save()
                return redirect('events:event-detail', pk=event.pk)
            else:
                context = self.get_context_data(review_form=review_form)
                return self.render_to_response(context)

        return super().get(request, *args, **kwargs)


@require_POST
def create_review(request):
    data = {}
    if request.user and request.user.is_authenticated:
        event_id = request.POST.get('key', '')
        event = Event.objects.get(id=event_id)
        rate = request.POST.get('rate', '')
        text = request.POST.get('text', '')

        review = Review(event=event, rate=rate, text=text)
        review.user = request.user
        review.save()

        data = {
            'ok': True,
            'msg': '',
            'rate': rate,
            'text': text,
            'created': review.created,
            'user_name': review.user.username,
        }
    else:
        data = {
            'ok': False,
            'msg': 'Отзывы могут оставлять только зарегистрированные пользователи',
        }
    return JsonResponse(data)


class EventUpdateView(UpdateView):
    model = Event
    template_name = 'events/event_update.html'
    form_class = EventUpdateForm
    context_object_name = 'event'

    def get_object(self, queryset=None):
        default_object = super().get_object(queryset)
        return default_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = self.object
        context['users'] = Enroll.objects.filter(event=self.object.id)
        context['reviews'] = Review.objects.filter(event=self.object.id)
        return context


class EventCreateView(CreateView):
    model = Event
    template_name = 'events/event_create.html'
    form_class = EventCreationForm
    success_url = reverse_lazy('events:index')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('events:login')  # Перенаправляем неаутентифицированных пользователей на страницу входа
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Новое событие было успешно создано')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        return super().form_invalid(form)


class EventDeleteView(DeleteView):
    model = Event
    template_name = 'events/event_update.html'
    success_url = reverse_lazy('events:index')

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        messages.success(request, f'Событие {self.object} удалено')
        return result


class SignupView(View):
    template_name = 'events/signup.html'
    form_class = CustomUserCreationForm

    def get(self, request):
        form = self.form_class()
        form.fields['username'].widget.attrs['class'] = 'form-control'
        form.fields['email'].widget.attrs['class'] = 'form-control'
        form.fields['password1'].widget.attrs['class'] = 'form-control'
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        return render(request, self.template_name, {'form': form})


class LoginView(LoginView):
    form_class = LoginForm
    template_name = 'events/login.html'


class MailView(View):
    template_name = 'events/mail.html'

    def get(self, request):
        subscriber_form = SubscriberForm()  # Создайте экземпляр формы

        # Получите список всех подписчиков
        subscribers = Subscriber.objects.all()

        return render(request, 'events/mail.html', {'subscriber_form': subscriber_form, 'subscribers': subscribers})


class SendEmailView(View):
    def post(self, request):
        email_form = MailForm(request.POST)

        if email_form.is_valid():
            # Проверяем наличие активных подписчиков
            subscribers = Subscriber.objects.filter(active=True)
            if subscribers:
                subject = email_form.cleaned_data['subject']
                message = email_form.cleaned_data['message']
                from_email = 'indeterminateveb@gmail.com'
                recipient_list = [subscriber.email for subscriber in subscribers]

                try:
                    send_mail(subject, message, from_email, recipient_list)
                    return JsonResponse({'success': 'Emails sent successfully'})
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=500)
            else:
                return JsonResponse({'error': 'No active subscribers found'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid form data'}, status=400)


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'events/change_password.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('events:index')
    login_url = 'events:login'  # Используйте полный путь к URL-шаблону для страницы входа

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class CustomPasswordResetView(PasswordResetView):
    template_name = 'events/password_reset.html'
    email_template_name = 'events/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')  # Используйте reverse_lazy для получения URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['uid'] = urlsafe_base64_encode(force_bytes(self.request.user.pk))
            context['token'] = default_token_generator.make_token(self.request.user)
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('events:login')  # Перенаправляем неаутентифицированных пользователей на страницу входа
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user_email = form.cleaned_data['email']
        user = User.objects.get(email=user_email)
        context = {
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user)
        }
        send_mail(
            subject="Сброс пароля",
            message="Ссылка для сброса пароля",
            from_email="indeterminateveb@gmail.com",
            recipient_list=[user_email],
            html_message=render_to_string(self.email_template_name, context)
        )
        return super().form_valid(form)


@login_required
def custom_password_reset(request):
    return CustomPasswordResetView.as_view()(request)


class PasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'events/password_reset_confirm.html'

    def get_success_url(self):
        return reverse_lazy('events:password_reset_complete')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('events:login')  # Замените 'events:login' на URL вашей страницы входа


def get_subscribers_view(request):
    subscribers = Subscriber.objects.all()
    data = {
        'subscribers': list(subscribers.values())
    }
    return JsonResponse(data)


class AddSubscriberView(View):
    template_name = 'events/mail.html'

    def get(self, request):
        users = User.objects.all()
        subscribers = Subscriber.objects.all()
        # Получить уникальные email'ы пользователей, исключая пустые значения
        emails = User.objects.exclude(email__isnull=True).exclude(email__exact='').values_list('email', flat=True).distinct()
        context = {
            'users': users,
            'subscribers': subscribers,
            'emails': emails
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user_id = request.POST.get('user')
        subscriber_email = request.POST.get('subscriber_email')

        # Проверяем, существует ли подписчик с таким email'ом
        if Subscriber.objects.filter(subscriber_email=subscriber_email).exists():
            return JsonResponse({'error': 'Subscriber with this email already exists.'}, status=400)

        # Получаем пользователя по его id
        user = User.objects.get(id=user_id)

        # Создаем нового подписчика и связываем его с пользователем
        subscriber = Subscriber.objects.create(subscriber_email=subscriber_email, user=user)

        subscribers = Subscriber.objects.all()

        context = {
            'subscribers': subscribers,
            'users': User.objects.all()  # Добавляем список пользователей в контекст
        }

        return render(request, self.template_name, context)


class DeleteSubscriberView(View):

    def post(self, request, subscriber_id):  # Добавьте параметр subscriber_id
        try:
            subscriber = Subscriber.objects.get(id=subscriber_id)
            subscriber.delete()
        except Subscriber.DoesNotExist:
            return JsonResponse({'error': 'Subscriber not found.'}, status=404)

        subscribers = Subscriber.objects.all()

        return render(request, 'events/mail.html', {'subscribers': subscribers})


class ProfileView(LoginRequiredMixin, View):
    template_name = 'events/profile.html'

    def get(self, request):
        user = request.user
        custom_user = CustomUser.objects.get(user=user)
        avatar_form = AvatarForm(instance=custom_user)
        username_form = UsernameForm(instance=user)
        email_form = EmailForm(instance=user)

        enrolls = Enroll.objects.filter(user=request.user).select_related('event').select_related('review')

        reviews = Review.objects.filter(user=user)

        # Вычислить среднюю оценку всех пользователей
        average_rating = round(Review.objects.aggregate(Avg('rate'))['rate__avg'], 1)

        return render(request, self.template_name, {'avatar_form': avatar_form, 'username_form': username_form,
                                                    'email_form': email_form, 'custom_user': custom_user,
                                                    'email': user.email,
                                                    'username': user.username, 'user': user, 'enrolls': enrolls,
                                                    'reviews': reviews, 'average_rating': average_rating})

    def post(self, request):
        user = request.user
        custom_user = CustomUser.objects.get(user=user)
        avatar_form = AvatarForm(request.POST, request.FILES, instance=custom_user)
        username_form = UsernameForm(request.POST, instance=user)
        email_form = EmailForm(request.POST, instance=user)

        if 'avatar_form_submit' in request.POST:
            if avatar_form.is_valid():
                avatar_form.save()

        if 'username_form_submit' in request.POST:
            if username_form.is_valid():
                if 'username' in username_form.cleaned_data and username_form.cleaned_data['username']:
                    user.username = username_form.cleaned_data['username']
                    username_form.save()
                else:
                    user.username = user.username  # Оставляем текущее значение username

        if 'email_form_submit' in request.POST:
            if email_form.is_valid():
                user.email = email_form.cleaned_data['email']

        new_email = request.POST.get('email')  # Получаем новый email из POST запроса
        if new_email and new_email != user.email:
            user.email = new_email

        user.save()

        return redirect('events:profile')