from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views


urlpatterns = format_suffix_patterns([
    url(r'^gettoken/$',
        views.GetTokenApi.as_view(),
        name='login'),
    url(r'^updatetoken/$',
        views.UpdateTokenApi.as_view(),
        name='login'),
    url(r'^create/event/$',
        views.CreateEventApi.as_view(),
        name='createevent'),
    url(r'^start/trip/$',
        views.StartTripApi.as_view(),
        name='starttrip'),
    url(r'^stop/trip/$',
        views.StopTripApi.as_view(),
        name='stoptrip'),
    url(r'^check/event/$',
        views.CheckEventApi.as_view(),
        name='checkevent'),
    url(r'^upvote/event/$',
        views.UpvoteEventApi.as_view(),
        name='upvoteevent'),
    url(r'^downvote/event/$',
        views.DownvoteEventApi.as_view(),
        name='downvoteeventapi'),
])