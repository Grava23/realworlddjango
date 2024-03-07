from django.shortcuts import render, get_object_or_404
from events.models import Event, Review, Feature, Enroll, User, Category
from django.http import JsonResponse
from django.contrib import messages
from django.http import HttpResponseForbidden
from datetime import datetime
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.shortcuts import render
from .forms import EventUpdateForm, EventCreationForm
from django.urls import reverse_lazy


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

    def get_object(self, queryset=None):
        default_object = super().get_object(queryset)
        return default_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = self.object
        reviews = Review.objects.filter(event=self.object.id)
        context['reviews'] = reviews
        context['rate'] = self.object.rate(reviews)
        context['participants'] = 100 - self.object.participants_number

        if Event.is_private == True:
            context['private'] = 'private'
        else:
            context['private'] = 'is_available'

        return context


@require_POST
def create_review(request):
    data = {}
    if request.user and request.user.is_authenticated:
        created = str(datetime.date)
        rate = request.POST.get('rate', '')
        text = request.POST.get('text', '')
        data = {
                    'ok': True,  # True если отзыв создан успешно, False в противном случае,
                    'msg': '',         # Сообщение об ошибке
                    'rate': rate,        # Оценка отзыва
                    'text': text,        # Текст отзыва
                    'created': created,  # Дата создания отзыва в формате DD.MM.YYYY
                    'user_name': '',   # Полное имя пользователя
}
    else:
        print('Отзывы могут оставлять только зарегистрированные пользовател')
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
    success_url = reverse_lazy('events:event_list')

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden('Недостаточно прав для добавления нового объекта')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Новое событие было успешно')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        return super().form_invalid(form)


class EventDeleteView(DeleteView):
    model = Event
    template_name = 'events/event_update.html'
    success_url = reverse_lazy('events:event_list')

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        messages.success(request, f'Событие {self.object} удалено')
        return result

