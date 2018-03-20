# Generated by Django 2.0.1 on 2018-03-20 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bloodfinder', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donor',
            name='aadhar_number',
        ),
        migrations.RemoveField(
            model_name='donor',
            name='bhamasha_id',
        ),
        migrations.AddField(
            model_name='donor',
            name='lattitude',
            field=models.DecimalField(decimal_places=7, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='donor',
            name='longitude',
            field=models.DecimalField(decimal_places=7, default=0, max_digits=10),
            preserve_default=False,
        ),
    ]
