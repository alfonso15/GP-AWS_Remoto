import datetime
from .client import SQLHandler
from django.db import transaction
from tickets.models import SerialNumber
from tickets.serializers import SerialNumberSerializer


class SerialNumbersHandler(SQLHandler):

    def _get_serial_numbers_catalogue(self, customer_number, company):
        self.cursor.execute(
            f"SELECT SERLNMBR, EQUIPID, ADRSCODE, OFFID, SVCAREA, TECHID, TIMEZONE FROM SVC00300 WHERE CUSTNMBR = {customer_number}"
        )
        query = self.cursor.fetchall()
        data = []

        for row in query:
            data.append({
                'id': f"{customer_number}#-#{row.EQUIPID}",
                'name': row.SERLNMBR.strip(),
            })
        return data

    def get_serial_numbers(self, company):
        if company:
            if self.cursor:
                return self._get_serial_numbers_catalogue(company.customer_number, company)
            serializer = SerialNumberSerializer(SerialNumber.objects.filter(company=company), many=True)
            return serializer.data
