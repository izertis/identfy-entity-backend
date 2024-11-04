from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand

from credentials.models import (
    IssuedVerifiableCredential,
    StatusList2021,
)
from openid.models import (
    IssuanceFlow,
    IssuanceInformation,
    NonceManager,
    PresentationDefinition,
    VerifyFlow,
)


class Command(BaseCommand):
    help = "Populate db with default roles and permissions."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            print("Creating permissions and user groups.")
            services = Group.objects.filter(
                name="SERVICE"
            ).first() or Group.objects.create(name="SERVICE")
            users = Group.objects.filter(name="VIEWER").first() or Group.objects.create(
                name="VIEWER"
            )
            admins = Group.objects.filter(name="OWNER").first() or Group.objects.create(
                name="OWNER"
            )

            print("Creating Openid permissions.")

            # Nonce Manager
            nonce_manager = ContentType.objects.get_for_model(NonceManager)
            view_permission = Permission.objects.get(
                codename="view_noncemanager", content_type=nonce_manager
            )
            add_permission = Permission.objects.get(
                codename="add_noncemanager", content_type=nonce_manager
            )
            change_permission = Permission.objects.get(
                codename="change_noncemanager", content_type=nonce_manager
            )
            delete_permission = Permission.objects.get(
                codename="delete_noncemanager", content_type=nonce_manager
            )

            services.permissions.add(
                view_permission, add_permission, change_permission, delete_permission
            )
            services.save()

            # Issuance Flow
            issuance_flow = ContentType.objects.get_for_model(IssuanceFlow)
            view_permission = Permission.objects.get(
                codename="view_issuanceflow", content_type=issuance_flow
            )
            add_permission = Permission.objects.get(
                codename="add_issuanceflow", content_type=issuance_flow
            )
            change_permission = Permission.objects.get(
                codename="change_issuanceflow", content_type=issuance_flow
            )
            delete_permission = Permission.objects.get(
                codename="delete_issuanceflow", content_type=issuance_flow
            )
            services.permissions.add(view_permission)
            services.save()

            users.permissions.add(view_permission)
            users.save()
            admins.permissions.add(
                view_permission, add_permission, change_permission, delete_permission
            )
            admins.save()

            # Issuance Information
            issuance_info = ContentType.objects.get_for_model(IssuanceInformation)
            view_permission = Permission.objects.get(
                codename="view_issuanceinformation", content_type=issuance_info
            )
            add_permission = Permission.objects.get(
                codename="add_issuanceinformation", content_type=issuance_info
            )
            change_permission = Permission.objects.get(
                codename="change_issuanceinformation", content_type=issuance_info
            )
            delete_permission = Permission.objects.get(
                codename="delete_issuanceinformation", content_type=issuance_info
            )
            services.permissions.add(view_permission)
            services.save()

            users.permissions.add(view_permission)
            users.save()
            admins.permissions.add(
                view_permission, add_permission, change_permission, delete_permission
            )
            admins.save()

            # Verify Flow
            verify_flow = ContentType.objects.get_for_model(VerifyFlow)
            view_permission = Permission.objects.get(
                codename="view_verifyflow", content_type=verify_flow
            )
            add_permission = Permission.objects.get(
                codename="add_verifyflow", content_type=verify_flow
            )
            change_permission = Permission.objects.get(
                codename="change_verifyflow", content_type=verify_flow
            )
            delete_permission = Permission.objects.get(
                codename="delete_verifyflow", content_type=verify_flow
            )

            users.permissions.add(view_permission)
            users.save()
            admins.permissions.add(
                view_permission, add_permission, change_permission, delete_permission
            )
            admins.save()

            # Presentation Definition
            presentation_flow = ContentType.objects.get_for_model(
                PresentationDefinition
            )
            view_permission = Permission.objects.get(
                codename="view_presentationdefinition", content_type=presentation_flow
            )
            add_permission = Permission.objects.get(
                codename="add_presentationdefinition", content_type=presentation_flow
            )
            change_permission = Permission.objects.get(
                codename="change_presentationdefinition", content_type=presentation_flow
            )
            delete_permission = Permission.objects.get(
                codename="delete_presentationdefinition", content_type=presentation_flow
            )
            services.permissions.add(view_permission)
            services.save()

            users.permissions.add(view_permission)
            users.save()
            admins.permissions.add(
                view_permission, add_permission, change_permission, delete_permission
            )
            admins.save()

            print("Creating Credentials permissions.")

            # Issued Verifiable Credentials
            issued_verifiable_credentials = ContentType.objects.get_for_model(
                IssuedVerifiableCredential
            )
            view_permission = Permission.objects.get(
                codename="view_issuedverifiablecredential",
                content_type=issued_verifiable_credentials,
            )
            add_permission = Permission.objects.get(
                codename="add_issuedverifiablecredential",
                content_type=issued_verifiable_credentials,
            )
            change_permission = Permission.objects.get(
                codename="change_issuedverifiablecredential",
                content_type=issued_verifiable_credentials,
            )
            delete_permission = Permission.objects.get(
                codename="delete_issuedverifiablecredential",
                content_type=issued_verifiable_credentials,
            )

            users.permissions.add(view_permission)
            users.save()
            admins.permissions.add(
                view_permission, add_permission, change_permission, delete_permission
            )
            admins.save()

            # Status List
            status_list = ContentType.objects.get_for_model(StatusList2021)
            view_permission = Permission.objects.get(
                codename="view_statuslist2021",
                content_type=status_list,
            )
            add_permission = Permission.objects.get(
                codename="add_statuslist2021",
                content_type=status_list,
            )
            change_permission = Permission.objects.get(
                codename="change_statuslist2021",
                content_type=status_list,
            )
            delete_permission = Permission.objects.get(
                codename="delete_statuslist2021",
                content_type=status_list,
            )

            services.permissions.add(
                view_permission, add_permission, change_permission, delete_permission
            )
            services.save()

            print("Creating Django permissions.")

            # Users
            users_perm = ContentType.objects.get_for_model(User)
            view_permission = Permission.objects.get(
                codename="view_user", content_type=users_perm
            )
            add_permission = Permission.objects.get(
                codename="add_user", content_type=users_perm
            )
            change_permission = Permission.objects.get(
                codename="change_user", content_type=users_perm
            )
            delete_permission = Permission.objects.get(
                codename="delete_user", content_type=users_perm
            )
            users.permissions.add(view_permission)
            users.save()

            admins.permissions.add(view_permission)
            admins.save()

            # Groups
            groups = ContentType.objects.get_for_model(Group)
            view_permission = Permission.objects.get(
                codename="view_group", content_type=groups
            )
            add_permission = Permission.objects.get(
                codename="add_group", content_type=groups
            )
            change_permission = Permission.objects.get(
                codename="change_group", content_type=groups
            )
            delete_permission = Permission.objects.get(
                codename="delete_group", content_type=groups
            )

            admins.permissions.add(
                view_permission,
            )
            admins.save()

            # Log
            log = ContentType.objects.get_for_model(LogEntry)
            view_permission = Permission.objects.get(
                codename="view_logentry", content_type=log
            )
            add_permission = Permission.objects.get(
                codename="add_logentry", content_type=log
            )
            change_permission = Permission.objects.get(
                codename="change_logentry", content_type=log
            )
            delete_permission = Permission.objects.get(
                codename="delete_logentry", content_type=log
            )

            admins.permissions.add(
                view_permission,
            )
            admins.save()

            users.permissions.add(
                view_permission,
            )
            users.save()

            # Session
            session = ContentType.objects.get_for_model(Session)
            view_permission = Permission.objects.get(
                codename="view_session", content_type=session
            )
            add_permission = Permission.objects.get(
                codename="add_session", content_type=session
            )
            change_permission = Permission.objects.get(
                codename="change_session", content_type=session
            )
            delete_permission = Permission.objects.get(
                codename="delete_session", content_type=session
            )

            admins.permissions.add(
                view_permission, add_permission, change_permission, delete_permission
            )
            admins.save()

            users.permissions.add(
                view_permission, add_permission, change_permission, delete_permission
            )
            users.save()
            print("Success.")
        except Exception as e:
            print("Operation failed because: " + str(e))
