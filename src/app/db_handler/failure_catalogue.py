import datetime
from .client import SQLHandler
from django.db import transaction
from tickets.models import FailureCatalogue
from tickets.serializers import FailureCatalogueSerializer


class FailureCatalogueHandler(SQLHandler):
    failure_catalogue_last_update = None

    def _get_failure_catalogue(self):
        self.cursor.execute("SELECT PROBCDE, DSCRIPTN, DEX_ROW_ID  FROM SVC00907")
        query = self.cursor.fetchall()
        data = []
        for row in query:
            desc = row.DSCRIPTN.strip()
            if len(desc) > 3:
                data.append({
                    'name': desc,
                    'id': row.DEX_ROW_ID,
                })
        self._update_catalogue_attrs(datetime.date.today(), query)

    @classmethod
    def _update_catalogue_attrs(cls, date, query):
        with transaction.atomic():
            for row in query:
                desc = row.DSCRIPTN.strip()
                if len(desc) > 3:
                    FailureCatalogue.objects.update_or_create(
                        failure_id=row.DEX_ROW_ID,
                        defaults={'failure_description': row.DSCRIPTN.strip(), 'probcde': row.PROBCDE}
                    )
        cls.failure_catalogue_last_update = date

    def get_failures_catalogue(self):
        if self.failure_catalogue_last_update != datetime.date.today() and self.cursor is not None:
            self._get_failure_catalogue()
        serializer = FailureCatalogueSerializer(FailureCatalogue.objects.all(), many=True)
        return serializer.data
