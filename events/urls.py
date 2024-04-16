from . import views
from django.urls import path, include
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetCompleteView
from .views import SignupView, IndexView, LoginView, ProfileView, CustomPasswordChangeView, LogoutView
from .views import SendEmailView, CustomPasswordResetView, PasswordResetConfirmView, MailView, get_subscribers_view
from .views import AddSubscriberView
from .views import ProfileView
from django.conf import settings
from django.conf.urls.static import static


app_name = 'events'

urlpatterns = [
    path('list/', views.EventListView.as_view(), name='event_list'),
    path('detail/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('event-update/<int:pk>/', views.EventUpdateView.as_view(), name='event_update'),
    path('event-delete/<int:pk>/', views.EventDeleteView.as_view(), name='event_delete'),
    path('event-create/', views.EventCreateView.as_view(), name='event_create'),
    path('', IndexView.as_view(), name='index'),
    path('accounts/', include('allauth.urls')),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('mail/', MailView.as_view(), name='mail'),
    path('change-password/', CustomPasswordChangeView.as_view(), name='change_password'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('send_email/', SendEmailView.as_view(), name='send_email'),
    path('get_subscribers/', get_subscribers_view, name='get_subscribers'),
    path('add_subscriber/', AddSubscriberView.as_view(), name='add_subscriber'),
    path('delete_subscriber/<int:subscriber_id>/', views.DeleteSubscriberView.as_view(), name='delete_subscriber'),
    path('events/detail/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),

]

# Добавляем обработчики для медиафайлов
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)