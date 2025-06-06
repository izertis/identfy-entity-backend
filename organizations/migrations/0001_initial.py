# Generated by Django 5.1 on 2025-03-25 15:25

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationKeys',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Name')),
                ('type', models.CharField(choices=[('rsa', 'rsa'), ('secp256k1', 'secp256k1'), ('secp256r1', 'secp256r1')], default='secp256k1', max_length=20, verbose_name='Type')),
                ('format', models.CharField(choices=[('jwk', 'jwk'), ('hex', 'hex')], default='jwk', max_length=100, verbose_name='Format')),
                ('value', models.JSONField(default=dict, help_text='Add here you Private Key or your information to search it', max_length=2000, verbose_name='Value')),
            ],
            options={
                'verbose_name': 'Organization Keys',
                'verbose_name_plural': 'Organization Keys',
            },
        ),
    ]
