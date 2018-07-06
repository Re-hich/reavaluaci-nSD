from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^items/$', views.items, name='items'),
    url(r'^items/(?P<category>.*)/$', views.items, name='items'),
    url(r'^item/(\d+)/$', views.item, name='item'),
    url(r'^shoppingcart/$', views.shoppingcart, name='shoppingcart'),
    url(r'^buy/$', views.buy, name='buy'),
    url(r'^bought/$', views.bought, name='bought'),
    url(r'^register/$', views.register, name='register'),
    url(r'^comparator/$', views.comparator, name='comparator')

]
