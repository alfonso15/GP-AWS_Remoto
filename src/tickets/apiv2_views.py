from app.db_handler.create_ticket import CreateTicketHandler
from django.http import HttpResponseRedirect
from tickets.models import Ticket
from django.views.generic import (
    FormView,
    TemplateView
)
from django import forms


class UpdateCommentSuccess(TemplateView):
    content_type = 'text/json'
    template_name = 'json.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'json':'{"status":"success"}'
        })
        return context


class UpdateCommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)


class UpdateComment(FormView):
    form_class = UpdateCommentForm
    template_name = 'json.html'
    success_url = '/api/v2/ticket/comment/update/success'

    def form_valid(self, form):
        ticket_id = self.kwargs.get('report_id', None)
        if not ticket_id:
            raise ValueError('Ticket ID not defined')
        ticket = Ticket.objects.get(report_id=ticket_id)

        comment = form.cleaned_data['comment']
        if not comment:
            raise ValueError('Comment not defined')

        ticket.comments += comment
        ticket.save()

        CreateTicketHandler()._update_comment_data(ticket)

        return super().form_valid(form)
