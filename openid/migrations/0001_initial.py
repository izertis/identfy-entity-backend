# Generated by Django 4.1.3 on 2024-03-06 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CredentialIssuerMetadata',
            fields=[
                ('issuer', models.CharField(default='did:ebsi:ziDnioxYYLW1a3qUbqTFz4W', max_length=200, primary_key=True, serialize=False, verbose_name='Issuer')),
                ('authorization_server', models.CharField(blank=True, max_length=200, null=True, verbose_name='Authorization Server')),
                ('credential_issuer', models.CharField(blank=True, max_length=200, null=True, verbose_name='Credential Issuer')),
                ('credential_endpoint', models.CharField(blank=True, max_length=200, null=True, verbose_name='Credential Endpoint')),
                ('deferred_credential_endpoint', models.CharField(blank=True, max_length=200, null=True, verbose_name='Deferred Credential Endpoint')),
                ('credentials_supported', models.JSONField(verbose_name='Supported Credentials')),
            ],
            options={
                'verbose_name': 'Credential Issuer Metadata',
                'verbose_name_plural': 'Credential Issuers Metadata',
            },
        ),
        migrations.CreateModel(
            name='IssuanceCredentialOffer',
            fields=[
                ('issuer', models.CharField(default='did:ebsi:ziDnioxYYLW1a3qUbqTFz4W', max_length=200, primary_key=True, serialize=False, verbose_name='Issuer')),
                ('credentials_supported', models.JSONField(verbose_name='Supported Credentials')),
                ('credential_offer', models.CharField(max_length=2500, verbose_name='Credential Offer')),
                ('timestamp', models.DateTimeField(auto_now=True, verbose_name='Timestamp')),
                ('qr', models.URLField(verbose_name='QR')),
            ],
            options={
                'verbose_name': 'Issuance Credential Offer',
                'verbose_name_plural': 'Issuance Credential Offers',
            },
        ),
        migrations.CreateModel(
            name='NonceManager',
            fields=[
                ('nonce', models.CharField(max_length=2000, primary_key=True, serialize=False, verbose_name='Nonce')),
                ('state', models.JSONField(blank=True, null=True, verbose_name='State')),
                ('did', models.CharField(max_length=200, verbose_name='Did')),
            ],
            options={
                'verbose_name': 'Nonce Manager',
                'verbose_name_plural': 'Nonces Manager',
            },
        ),
        migrations.CreateModel(
            name='PresentationDefinition',
            fields=[
                ('id', models.CharField(max_length=2500, primary_key=True, serialize=False, verbose_name='Identifier')),
                ('scope', models.CharField(max_length=100, unique=True, verbose_name='Scope')),
                ('content', models.JSONField(verbose_name='Content')),
            ],
            options={
                'verbose_name': 'Presentation Definition',
                'verbose_name_plural': 'Presentation Definitions',
            },
        ),
        migrations.CreateModel(
            name='VPScopeAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scope', models.CharField(max_length=2000, verbose_name='Scope')),
                ('response_type', models.CharField(choices=[('vp_token', 'vp_token'), ('id_token', 'id_token')], default='vp_token', max_length=100, verbose_name='Response Type')),
                ('entity', models.CharField(default='did:ebsi:ziDnioxYYLW1a3qUbqTFz4W', editable=False, max_length=200, verbose_name='Entity')),
                ('presentation_definition', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='openid.presentationdefinition')),
            ],
            options={
                'verbose_name': 'VP Scope Action',
                'verbose_name_plural': 'VP Scope Actions',
            },
        ),
        migrations.CreateModel(
            name='VerifierMetadata',
            fields=[
                ('verifier', models.CharField(default='did:ebsi:ziDnioxYYLW1a3qUbqTFz4W', max_length=200, primary_key=True, serialize=False, verbose_name='Verifier')),
                ('authorization_server', models.CharField(blank=True, max_length=200, null=True, verbose_name='Authorization Server')),
                ('scope', models.CharField(max_length=200, verbose_name='Scope')),
                ('presentation_definition_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='openid.presentationdefinition')),
            ],
            options={
                'verbose_name': 'Verifier Metadata',
                'verbose_name_plural': 'Verifiers Metadata',
            },
        ),
        migrations.CreateModel(
            name='VCScopeAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scope', models.CharField(default='openid', max_length=2000, verbose_name='Scope')),
                ('response_type', models.CharField(choices=[('vp_token', 'vp_token'), ('id_token', 'id_token')], default='id_token', max_length=100, verbose_name='Response Type')),
                ('is_deferred', models.BooleanField(default=False, verbose_name='Deferred')),
                ('credential_types', models.CharField(max_length=2000, verbose_name='Credential Type')),
                ('credential_schema_address', models.CharField(max_length=2000, verbose_name='Credential Schema')),
                ('entity', models.CharField(default='did:ebsi:ziDnioxYYLW1a3qUbqTFz4W', max_length=200, verbose_name='Entity')),
                ('presentation_definition', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='openid.presentationdefinition')),
            ],
            options={
                'verbose_name': 'VC Scope Action',
                'verbose_name_plural': 'VC Scope Actions',
            },
        ),
    ]