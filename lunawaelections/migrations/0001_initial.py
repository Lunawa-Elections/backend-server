# Generated by Django 3.2.25 on 2024-04-16 16:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AndroidID',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('counter', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loc', models.CharField(max_length=50)),
                ('name', models.CharField(default='', max_length=255)),
                ('vaas', models.CharField(default='', max_length=255)),
                ('votes', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('status', models.CharField(default='Uploaded', max_length=50)),
                ('voted_members', models.JSONField(default=list)),
                ('android_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lunawaelections.androidid')),
            ],
        ),
    ]
