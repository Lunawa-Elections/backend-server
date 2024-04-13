# Generated by Django 3.2.25 on 2024-04-13 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunawaelections', '0002_image_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='vaas',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='image',
            name='status',
            field=models.CharField(default='Uploaded', max_length=50),
        ),
        migrations.AlterField(
            model_name='member',
            name='loc',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='member',
            name='name',
            field=models.CharField(default='', max_length=255),
        ),
    ]
