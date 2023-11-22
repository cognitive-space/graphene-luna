from django.urls import path

import lunastarter.ws

urlpatterns = [
  path('graphql', lunastarter.ws.WSHandler),
]
