from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('list/', views.EventListView.as_view(), name='event_list'),
    path('detail/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('event-update/<int:pk>/', views.EventUpdateView.as_view(), name='event_update'),
    path('event-delete/<int:pk>/', views.EventDeleteView.as_view(), name='event_delete'),
    path('event-create/', views.EventCreateView.as_view(), name='event_create'),

]



