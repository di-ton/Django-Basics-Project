from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView

from accounts.models import User, ScientistProfile
from messaging.forms import ProjectMessageForm
from messaging.models import MessageRecipient, Message
from projects.models import Project


class InboxView(LoginRequiredMixin, ListView):
    model = MessageRecipient
    template_name = "messaging/inbox.html"
    context_object_name = "messages"

    def get_queryset(self):
        return (
            MessageRecipient.objects
            .filter(recipient=self.request.user)
            .exclude(message__sender=self.request.user)
            .select_related("message", "message__sender")
            .order_by("-message__created_at")
        )


class SentMessagesView(LoginRequiredMixin, ListView):
    model = MessageRecipient
    template_name = "messaging/sent-messages.html"
    context_object_name = "messages"

    def get_queryset(self):
        return (
            MessageRecipient.objects
            .filter(recipient=self.request.user, message__sender=self.request.user)
            .select_related("message", "message__sender")
            .order_by("-message__created_at")
        )

class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "messaging/message-detail.html"

    def get_object(self):
        message = super().get_object()

        if not (
            message.sender == self.request.user
            or message.recipients.filter(pk=self.request.user.pk).exists()
        ):
            raise PermissionDenied

        MessageRecipient.objects.filter(
            message=message,
            recipient=self.request.user
        ).update(is_read=True)

        return message



class SendMessageView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ["subject", "body"]
    template_name = "messaging/send-message.html"

    def dispatch(self, request, *args, **kwargs):
        profile = get_object_or_404(ScientistProfile, slug=kwargs["slug"])
        # self.recipient_profile = profile
        self.recipient = profile.user
        return super().dispatch(request, *args, **kwargs)


    def form_valid(self, form):
        message = form.save(commit=False)
        message.sender = self.request.user
        message.save()


        # recipient inbox
        MessageRecipient.objects.create(
            message=message,
            recipient=self.recipient
        )

        # sender sent copy
        MessageRecipient.objects.create(
            message=message,
            recipient=self.request.user,
            is_read = True
        )

        return redirect("inbox")


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipient"] = self.recipient
        return context


class ProjectMessageView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = ProjectMessageForm
    template_name = "messaging/project-message.html"

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, slug=kwargs["slug"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["project"] = self.project
        return kwargs

    def form_valid(self, form):
        message = form.save(commit=False)
        message.sender = self.request.user
        message.project = self.project
        message.save()

        recipients = form.cleaned_data["recipients"]

        for user in recipients:
            MessageRecipient.objects.create(
                message=message,
                recipient=user
            )
        # sender sent copy
        MessageRecipient.objects.create(
            message=message,
            recipient=self.request.user,
            is_read=True
        )

        return redirect("project-overview", slug=self.project.slug)


class ReplyMessageView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ["subject", "body"]
    template_name = "messaging/send-message.html"

    def dispatch(self, request, *args, **kwargs):
        self.original = get_object_or_404(Message, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {
            "subject": f"Re: {self.original.subject}"
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["original"] = self.original
        return context

    # def form_valid(self, form):
    #     message = form.save(commit=False)
    #     message.sender = self.request.user
    #     message.subject = f"Re: {self.original.subject}"
    #
    #     message.is_report = self.original.is_report
    #     message.save()
    #
    #     # MessageRecipient.objects.create(
    #     #     message=message,
    #     #     recipient=self.original.sender
    #     # )
    #
    #     if self.original.sender == self.request.user:
    #         recipient = self.original.recipients.first()
    #     else:
    #         recipient = self.original.sender
    #
    #     # recipient inbox
    #     MessageRecipient.objects.create(
    #         message=message,
    #         recipient=recipient
    #     )
    #
    #     # sender sent
    #     MessageRecipient.objects.create(
    #         message=message,
    #         recipient=self.request.user,
    #         is_read=True
    #     )
    #
    #     return redirect("inbox")

    def form_valid(self, form):
        message = form.save(commit=False)
        message.sender = self.request.user
        message.subject = f"Re: {self.original.subject}"
        message.is_report = self.original.is_report
        message.save()

        if self.original.is_report:

            moderators = User.objects.filter(groups__name="Content Moderators")

            if self.request.user in moderators:
                # moderator replying → send to original user
                recipient = self.original.sender

                MessageRecipient.objects.create(
                    message=message,
                    recipient=recipient
                )

            else:
                # user replying → send to moderators
                for user in moderators:
                    if user != self.request.user:
                        MessageRecipient.objects.create(
                            message=message,
                            recipient=user
                        )

        else:
            # normal messaging
            if self.original.sender == self.request.user:
                recipient = self.original.recipients.first()
            else:
                recipient = self.original.sender

            MessageRecipient.objects.create(
                message=message,
                recipient=recipient
            )

        # sender copy (always)
        MessageRecipient.objects.create(
            message=message,
            recipient=self.request.user,
            is_read=True
        )

        return redirect("inbox")


# class DeleteMessageView(LoginRequiredMixin, View):
#
#     def post(self, request, pk):
#         message = get_object_or_404(Message, pk=pk)
#
#         if message.sender == request.user:
#             message.delete()
#         else:
#             MessageRecipient.objects.filter(
#                 message=message,
#                 recipient=request.user
#             ).delete()
#
#         return redirect("inbox")

# class DeleteMessageView(LoginRequiredMixin, View):
#
#     def post(self, request, pk):
#         message = get_object_or_404(Message, pk=pk)
#
#         # If user is sender → delete the message
#         if message.sender == request.user:
#             message.delete()
#         else:
#             # If user is recipient → remove from inbox
#             MessageRecipient.objects.filter(
#                 message=message,
#                 recipient=request.user
#             ).delete()
#
#         return redirect("inbox")

class DeleteMessageView(LoginRequiredMixin, View):

    def post(self, request, pk):
        message = get_object_or_404(Message, pk=pk)

        # delete sender copy
        if message.sender == request.user:
            MessageRecipient.objects.filter(
                message=message,
                recipient=request.user
            ).delete()

        # delete recipient copy
        else:
            MessageRecipient.objects.filter(
                message=message,
                recipient=request.user
            ).delete()

        return redirect("inbox")


class ReportProjectView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ["subject", "body"]
    template_name = "messaging/report-project.html"

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, slug=kwargs["slug"])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {
            "subject": f"Report: {self.project.title}"
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project
        return context


    def form_valid(self, form):
        message = form.save(commit=False)
        message.sender = self.request.user
        message.project = self.project
        message.is_report = True
        message.save()

        # send to Content Moderators
        moderators = User.objects.filter(groups__name="Content Moderators")

        for user in moderators:
            MessageRecipient.objects.create(
                message=message,
                recipient=user
            )

        # sender copy
        MessageRecipient.objects.create(
            message=message,
            recipient=self.request.user,
            is_read=True
        )

        return redirect("project-overview", slug=self.kwargs["slug"])



