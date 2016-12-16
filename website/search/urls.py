from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # ex: /polls/5/results/
    url(r'results/$', views.es_get_name),
    url(r'results-get/(.+)/$', views.choose_es_get_name)
]