from django.contrib import admin, messages
from sentry_sdk import capture_exception
from app.db_handler.create_ticket import CreateTicketHandler
from .models import Ticket, FailureCatalogue, SerialNumber, TicketFile


class TicketFileInline(admin.StackedInline):
    model = TicketFile
    extra = 1


@admin.register(Ticket)
class Admin(admin.ModelAdmin):
    list_display = ['report_id', 'status', 'company', 'serial_number', 'report_date', 'end_date', 'insert_200',
                    'insert_201', 'insert_202', "insert_SY03900"]
    readonly_fields = ['report_id', 'description', 'status', 'company', 'serial_number', 'serial_number_instance',
                       'report_date',
                       'failure_description', 'failure_instance', 'attention_date',
                       'end_date', 'name', 'last_name', 'email', 'phone', 'floor', 'area', 'counter', 'insert_200',
                       'insert_201', 'insert_202', 'insert_SY03900', 'comments', 'error_detail']
    list_filter = ["status", "company"]
    search_fields = ["report_id"]
    fields = readonly_fields + ['file']
    actions = ['retry_ticket_insert', 'truncate_description', 'truncate_name', 'retry_comment_insert']
    inlines = [TicketFileInline]

    def retry_comment_insert(self, request, queryset):
        errors = {}
        success_count = 0
        for ticket in queryset:
            try:
                CreateTicketHandler()._register_or_update_comment_data(ticket)
                success_count += 1
            except Exception as e:
                errors[ticket.report_id if ticket.report_id else ticket.pk] = str(e)
                capture_exception(e)
        if success_count >= 1:
            self.message_user(request, f"{success_count} tickets actualizados", messages.SUCCESS)

        self.message_user(request, errors, messages.ERROR)

    def retry_ticket_insert(self, request, queryset):
        errors = {}
        success_count, ignored = 0, 0
        for ticket in queryset:
            if ticket.insert_200 and ticket.insert_201 and ticket.insert_202 and ticket.insert_SY03900:
                ignored += 1
            else:
                try:
                    CreateTicketHandler().create_ticket(ticket)
                    success_count += 1
                except Exception as e:
                    errors[ticket.report_id if ticket.report_id else ticket.pk] = str(e)
                    capture_exception(e)
        if success_count >= 1:
            self.message_user(request, f"{success_count} tickets registrados", messages.SUCCESS)
        if ignored >= 1:
            self.message_user(request, f"{ignored} tickets ya estaban registrados", messages.SUCCESS)
        self.message_user(request, errors, messages.ERROR)

    def truncate_description(self, request, queryset):
        for item in queryset:
            item.description = item.description[:59]
            item.save()

    def truncate_name(self, request, queryset):
        for item in queryset:
            item.name = item.name[:20]
            item.save()


@admin.register(FailureCatalogue)
class Admin(admin.ModelAdmin):
    list_display = ['id', 'failure_id', 'failure_description']
    readonly_fields = ['failure_id', 'failure_description', 'probcde']


@admin.register(SerialNumber)
class Admin(admin.ModelAdmin):
    list_display = ['id', 'company', 'serial_number', 'serial_number_id']
    readonly_fields = ['company', 'serial_number', 'serial_number_id', 'adrscode', 'offid', 'svcarea', 'techid',
                       'timezone', 'itemnmbr']
