from django.db import models
from django.utils.timezone import now

expenditures = (
    ('Fuel', 'Fuel'),
    ('Transport', 'Transport'),
    ('Meals', 'Meals'),
    ('Out of Office', 'Out of Office'),
    ('Destination', 'Destination'),
    ('Others', 'Others')
)

class StaffReimbursement(models.Model):
    date = models.DateField(default=now)
    staff = models.ForeignKey('Staff.Staff', models.CASCADE, related_name='reimbursement_staff')
    description_of_assignment = models.TextField()
    expenditures = models.ManyToManyField('ExpenditurePurpose', blank=True)
    total = models.PositiveIntegerField(default=0)
    approved_by = models.ForeignKey('Staff.Staff', models.SET_NULL, null=True, blank=True)
    date_approved = models.DateTimeField(null=True, blank=True)


class ExpenditurePurpose(models.Model):
    reimbursement = models.ForeignKey('StaffReimbursement', models.CASCADE)
    attatchment = models.ForeignKey('Attatchment', models.SET_NULL, null=True, blank=True)
    expenditure = models.CharField(max_length=100, choices=expenditures)
    specification = models.CharField(max_length=100)
    daily_amount = models.PositiveIntegerField()
    days = models.PositiveIntegerField()
    total = models.PositiveIntegerField(default=0)


class Attatchment(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='attatchments/')


