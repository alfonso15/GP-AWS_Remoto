from django.core.management.base import BaseCommand, CommandError
from django.utils.datetime_safe import datetime
from datetime import timedelta

from app.db_handler.create_ticket import CreateTicketHandler
from tickets.models import Ticket


class Command(BaseCommand):
    help = "Update ticket with comment errors"

    def handle(self, *args, **options):
        yesterday = datetime.today() - timedelta(days=2)

        ticket_qs = Ticket.objects.filter(
            report_date__gte=yesterday,  # desde hace 2 dias
            insert_SY03900=False  # que no tengan un comentario creado o updateado
        )

        for ticket in ticket_qs:
            try:
                CreateTicketHandler()._register_or_update_comment_data(ticket)
            except Exception as e:
                print(e)
