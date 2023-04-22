from django.contrib.auth import get_user_model
from .models import Profile


class EmailAuthBackend:
    User = get_user_model()

    def authenticate(self, request, username, password):
        try:
            user = self.User.objects.get(email=username)
            if user.check_password(password):
                return user
            return None
        except (self.User.DoesNotExist, self.User.MultipleObjectsReturned,):
            return None

    def get_user(self, user_pk):
        try:
            return self.User.objects.get(pk=user_pk)
        except self.User.DoesNotExist:
            return None


def create_profile(backend, user, *args, **kwargs):
    Profile.objects.get_or_create(user=user)
