from django.db import models
from app.models import TimeStampedModel


class FailureCatalogue(models.Model):
    failure_id = models.CharField(max_length=64, db_index=True)
    failure_description = models.CharField(max_length=64)
    probcde = models.CharField(max_length=11, null=True)
    
    def __str__(self):
        return self.failure_description if self.failure_description else super(FailureCatalogue, self).__str__()
    

class SerialNumber(models.Model):
    company = models.ForeignKey('users.Company', on_delete=models.PROTECT, null=True)
    serial_number = models.CharField(max_length=64, db_index=True)
    serial_number_id = models.CharField(max_length=64, db_index=True, null=True)
    adrscode = models.CharField(max_length=15, null=True)
    offid = models.CharField(max_length=11, null=True)
    svcarea = models.CharField(max_length=11, null=True)
    techid = models.CharField(max_length=11, null=True)
    timezone = models.CharField(max_length=3, null=True)
    itemnmbr = models.CharField(max_length=32, null=True)

    def __str__(self):
        return f"{self.company.company_name} {self.serial_number}"


class Ticket(models.Model):
    company = models.ForeignKey('users.Company', on_delete=models.PROTECT, null=True)
    
    report_date = models.DateTimeField(auto_now_add=True)

    report_id = models.CharField(max_length=64, null=True, blank=True)

    serial_number_instance = models.ForeignKey('tickets.SerialNumber', on_delete=models.PROTECT, null=True)
    serial_number = models.CharField(max_length=64, db_index=True)
    serial_number_id = models.CharField(max_length=64, db_index=True, null=True)

    failure_instance = models.ForeignKey('tickets.FailureCatalogue', on_delete=models.PROTECT, null=True)
    failure_id = models.CharField(max_length=64)
    failure_description = models.CharField(max_length=64)

    description = models.CharField(max_length=60)
    name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True)
    floor = models.CharField(max_length=20, null=True)
    area = models.CharField(max_length=20, null=True)
    counter = models.CharField(max_length=20, null=True)
    
    comments = models.TextField(null=True, blank=True)
    
    techid = models.CharField(max_length=11, null=True)
    customer_reference = models.CharField(max_length=20, null=True)

    # Provided Data
    attention_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=5, null=True, blank=True)
    file = models.FileField(null=True, blank=True)


    #Insertion Verification
    insert_200 = models.BooleanField(default=False)
    insert_201 = models.BooleanField(default=False)
    insert_202 = models.BooleanField(default=False)
    insert_SY03900 = models.BooleanField(default=False)

    error_detail = models.TextField(null=True, editable=False)
    attempts = models.PositiveSmallIntegerField(null=True, default=0)
    
    class Meta:
        ordering = ('-report_date', '-pk')

    def save(self, *args, **kwargs):
        if self.report_id:
            self.report_id = self.report_id.strip()
        super(Ticket, self).save(*args, **kwargs)

    @property
    def full_name(self):
        output = self.name.strip() if self.name else ""
        output += " " + self.last_name.strip() if self.last_name else ""
        return output


class TicketFile(models.Model):
    ticket = models.ForeignKey("tickets.Ticket", on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    file = models.FileField(null=True, blank=True)
