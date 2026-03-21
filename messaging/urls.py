from django.urls import path

from messaging import views

urlpatterns = [
    path("inbox/", views.InboxView.as_view(), name="inbox"),
    path("sent/", views.SentMessagesView.as_view(), name="sent-messages"),
    path("send/<slug:slug>/", views.SendMessageView.as_view(), name="send-message"),
    path("<int:pk>/", views.MessageDetailView.as_view(), name="message-detail"),
    path("reply/<int:pk>/", views.ReplyMessageView.as_view(), name="reply-message"),
    path("delete/<int:pk>/", views.DeleteMessageView.as_view(), name="delete-message"),
    path("project/<slug:slug>/message/", views.ProjectMessageView.as_view(), name="project-message"),

    path("project/<slug:slug>/report/", views.ReportProjectView.as_view(), name="project-report"),
]