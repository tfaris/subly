from django.views.generic import RedirectView, TemplateView, FormView
from django.contrib.auth import login, logout
from django.core import urlresolvers

from mixins import TabViewMixin
from ..forms import AuthenticationForm


class IndexView(TemplateView, TabViewMixin):
    template_name = 'site/base.html'
    tab_id = 'home'


class LoginView(FormView, TabViewMixin):
    template_name = 'site/login.html'
    form_class = AuthenticationForm
    tab_id = 'login'

    def get_success_url(self):
        return urlresolvers.reverse('home')

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return super(LoginView, self).form_valid(form)


class LogoutView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return urlresolvers.reverse('login')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)
