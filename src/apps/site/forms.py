from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm, AuthenticationForm

from models import SiteUser


class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = SiteUser
        fields = ("email",)
