from django.urls import path
from . import apiv2_views

from django.views.decorators.csrf import csrf_exempt

app_name = 'api2'


urlpatterns = [
    path(
        'ticket/comment/update/success',
        apiv2_views.UpdateCommentSuccess.as_view(),
        name='ticket_update_comment_success'
    ),
    path(
        'ticket/<int:report_id>/comment/update',
        csrf_exempt(apiv2_views.UpdateComment.as_view()),
        name='ticket_update_comment'
    )
]
