# Django
from django.urls import path
from django.views.generic import TemplateView

# Local
from . import views

urlpatterns = [
    # Root
    path('', views.index, name='index',),

    # Footer
    path('about/', TemplateView.as_view(template_name='app/pages/about.html'), name='about',),
    path('faq/', TemplateView.as_view(template_name='app/pages/faq.html'), name='faq',),
    path('privacy/', TemplateView.as_view(template_name='app/pages/privacy.html'), name='privacy',),
    path('terms/', TemplateView.as_view(template_name='app/pages/terms.html'), name='terms',),
    path('support/', TemplateView.as_view(template_name='app/pages/support.html'), name='support',),

    # Authentication
    path('callback', views.callback, name='callback'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),

    # Account
    path('account', views.account, name='account',),
    path('thanks/', TemplateView.as_view(template_name='app/pages/thanks.html'), name='thanks',),

    # Delete
    path('delete', views.delete, name='delete',),

]
