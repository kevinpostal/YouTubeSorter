import google.oauth2.credentials
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from YoutubeAuth.utils import credentials_to_dict


class ValidateYoutubeToken(MiddlewareMixin):

    def process_request(self, request):
        if request.path == reverse("auth"):
            return
        if request.path.startswith(reverse("admin:index")):
            return
        if request.user.is_authenticated:
            if request.user.is_superuser:
                raise PermissionDenied()

            one_h_ago = timezone.now() - timezone.timedelta(hours=1)
            then = request.user.updated_at
            NUMBER_OF_SECONDS = 3600  # seconds in 1 hours

            if (one_h_ago - then).total_seconds() > NUMBER_OF_SECONDS:
                acct_creds = request.user.credentials_to_dict()
                credentials = google.oauth2.credentials.Credentials(**acct_creds)
                if credentials.valid:
                    new_request = google.auth.transport.requests.Request()
                    credentials.refresh(new_request)
                    get_user_model().objects.filter(
                        id=request.user.id,
                    ).update(**credentials_to_dict(credentials))
            return
        else:
            return
