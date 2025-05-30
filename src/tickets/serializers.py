import datetime
from django.db.models import Q
from rest_framework import serializers
from sentry_sdk import capture_exception
from app.db_handler.create_ticket import CreateTicketHandler
from users.models import Company
from .models import Ticket, FailureCatalogue, SerialNumber, TicketFile


class TicketFileSerializer(serializers.ModelSerializer):
    """
        Model to handle ticket files
    """
    class Meta:
        model = TicketFile
        fields = ["name", "file"]


class TicketSerializer(serializers.ModelSerializer):
    """
        Serializer for Ticket Model
    """
    failure_data = serializers.DictField(write_only=True)
    serial_number_data = serializers.DictField(write_only=True)
    file = serializers.SerializerMethodField(read_only=True)
    ticketfile_set = TicketFileSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        read_only_fields = ['report_id', 'report_date', 'attention_date', 'failure_description', 'serial_number',
                            'end_date', 'status', 'file', "ticketfile_set"]
        fields = ['serial_number_data', 'failure_data', 'description', 'name', 'last_name', 'email',
                  'phone', 'floor', 'area', 'counter', "comments"] + read_only_fields

    def get_file(self, instance):
        if instance.file:
            url = instance.file.url
            request = self.context.get('request')
            return f"https://{request.get_host()}{url}"

    def validate(self, attrs):
        failure_data = attrs.get('failure_data')
        serial_number_data = attrs.get('serial_number_data')

        try:
            serial_id = serial_number_data.get('id')
            customer_number, serial_number_id = serial_id.split("#-#")
        except ValueError:
            raise serializers.ValidationError(
                f"Error del sistema. \n Id {serial_id} inválido."
            )

        qs = Ticket.objects.filter(
            failure_id=failure_data.get('id'),
            serial_number_id=serial_number_id
        )

        qs = qs.filter(
            Q(end_date__lte=datetime.date(year=2000, day=1, month=1)) |
            Q(end_date__isnull=True)
        )
        if qs.exists():
            id_list = [t.report_id for t in qs.all()]
            raise serializers.ValidationError(
                f'Ya existe un ticket para {failure_data.get("name")} de este no. de serie: {", ".join(id_list)}'
            )
        return attrs

    def create(self, validated_data):
        failure_data = validated_data.pop('failure_data')
        serial_number_data = validated_data.pop('serial_number_data')

        validated_data['failure_description'] = failure_data.get('name')
        validated_data['failure_id'] = failure_data.get('id')
        validated_data['failure_instance'] = FailureCatalogue.objects.get(failure_id=failure_data.get('id'))

        customer_number, serial_number_id = serial_number_data.get('id').split("#-#")
        validated_data['serial_number'] = serial_number_data.get('name')
        validated_data['serial_number_id'] = serial_number_id

        customer = Company.objects.get(customer_number=int(customer_number))
        validated_data["company"] = customer

        instance = super(TicketSerializer, self).create(validated_data)

        # Handle Creation on SQL DB
        try:
            CreateTicketHandler().create_ticket(instance)
            instance.refresh_from_db()
        except Exception as e:
            capture_exception(e)
            instance.error_detail = str(e)

        instance.refresh_from_db()
        return instance


class TicketUpdateSerializer(serializers.ModelSerializer):
    """
        Serializer for update action
    """
    class Meta:
        model = Ticket
        fields = ['attention_date', 'end_date', 'status']


class FailureCatalogueSerializer(serializers.ModelSerializer):
    """
        Serializer for Failure Catalogue
    """
    id = serializers.CharField(source='failure_id')
    name = serializers.CharField(source='failure_description')

    class Meta:
        model = FailureCatalogue
        fields = ['name', 'id']


class SerialNumberSerializer(serializers.ModelSerializer):
    """
        Serializer for Failure Catalogue
    """
    id = serializers.CharField(source='serial_number_id')
    name = serializers.CharField(source='serial_number')

    class Meta:
        model = SerialNumber
        fields = ['name', 'id']
