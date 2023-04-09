from django.urls import path
from plotApp.views import process_csv
from plotApp.views import index

urlpatterns = [
    path('', index, name='index'),
    path('process_csv/', process_csv, name='process_csv'),
]
