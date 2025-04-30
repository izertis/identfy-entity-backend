from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand

from credentials.models import (
    IssuedVerifiableCredential,
    StatusList2021,
    VerifiableCredential,
)
from ebsi.models import (
    AccreditationToAccredit,
    AccreditationToAttest,
    AccreditationToOnboard,
    EbsiAccreditation,
    EbsiAccreditationWhiteList,
    PotentialAccreditationInformation,
)
from openid.models import (
    IssuanceFlow,
    IssuanceInformation,
    NonceManager,
    PresentationDefinition,
    VerifyFlow,
)
from organizations.models import OrganizationKeys


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

            print("Creating Organizations permissions.")

            # Organization Keys
            organization_keys = ContentType.objects.get_for_model(OrganizationKeys)
            view_permission = Permission.objects.get(
                codename="view_organizationkeys", content_type=organization_keys
            )
            add_permission = Permission.objects.get(
                codename="add_organizationkeys", content_type=organization_keys
            )
            change_permission = Permission.objects.get(
                codename="change_organizationkeys", content_type=organization_keys
            )
            delete_permission = Permission.objects.get(
                codename="delete_organizationkeys", content_type=organization_keys
            )
            users.permissions.add(view_permission)
            users.save()
            admins.permissions.add(
                view_permission, add_permission, change_permission, delete_permission
            )
            admins.save()
            services.permissions.add(view_permission)
            services.save()

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

            # Verifiable Credentials
            verifiable_credentials = ContentType.objects.get_for_model(
                VerifiableCredential
            )
            view_permission = Permission.objects.get(
                codename="view_verifiablecredential",
                content_type=verifiable_credentials,
            )
            add_permission = Permission.objects.get(
                codename="add_verifiablecredential",
                content_type=verifiable_credentials,
            )
            change_permission = Permission.objects.get(
                codename="change_verifiablecredential",
                content_type=verifiable_credentials,
            )
            delete_permission = Permission.objects.get(
                codename="delete_verifiablecredential",
                content_type=verifiable_credentials,
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

            print("Creating Ebsi permissions.")

            # PotentialAccreditationInformation
            potential_accreditation_information = ContentType.objects.get_for_model(
                PotentialAccreditationInformation
            )
            view_permission = Permission.objects.get(
                codename="view_potentialaccreditationinformation",
                content_type=potential_accreditation_information,
            )
            add_permission = Permission.objects.get(
                codename="add_potentialaccreditationinformation",
                content_type=potential_accreditation_information,
            )
            change_permission = Permission.objects.get(
                codename="change_potentialaccreditationinformation",
                content_type=potential_accreditation_information,
            )
            delete_permission = Permission.objects.get(
                codename="delete_potentialaccreditationinformation",
                content_type=potential_accreditation_information,
            )

            # admins.permissions.add(
            #     view_permission, add_permission, change_permission, delete_permission
            # )
            # admins.save()

            # EbsiAccreditation
            ebsi_accreditation = ContentType.objects.get_for_model(EbsiAccreditation)
            view_permission = Permission.objects.get(
                codename="view_ebsiaccreditation",
                content_type=ebsi_accreditation,
            )
            add_permission = Permission.objects.get(
                codename="add_ebsiaccreditation",
                content_type=ebsi_accreditation,
            )
            change_permission = Permission.objects.get(
                codename="change_ebsiaccreditation",
                content_type=ebsi_accreditation,
            )
            delete_permission = Permission.objects.get(
                codename="delete_ebsiaccreditation",
                content_type=ebsi_accreditation,
            )

            # admins.permissions.add(
            #     view_permission, add_permission, change_permission, delete_permission
            # )
            # admins.save()
            # EbsiAccreditationWhiteList
            ebsi_accreditation_white_list = ContentType.objects.get_for_model(
                EbsiAccreditationWhiteList
            )
            view_permission = Permission.objects.get(
                codename="view_ebsiaccreditationwhitelist",
                content_type=ebsi_accreditation_white_list,
            )

            add_permission = Permission.objects.get(
                codename="add_ebsiaccreditationwhitelist",
                content_type=ebsi_accreditation_white_list,
            )
            change_permission = Permission.objects.get(
                codename="change_ebsiaccreditationwhitelist",
                content_type=ebsi_accreditation_white_list,
            )
            delete_permission = Permission.objects.get(
                codename="delete_ebsiaccreditationwhitelist",
                content_type=ebsi_accreditation_white_list,
            )

            # admins.permissions.add(
            #     view_permission, add_permission, change_permission, delete_permission
            # )
            # admins.save()

            # AccreditationToAttest
            accreditation_to_attest = ContentType.objects.get(
                app_label=AccreditationToAttest._meta.app_label,
                model=AccreditationToAttest._meta.object_name.lower(),
            )

            view_permission = Permission.objects.get(
                codename="view_accreditationtoattest",
                content_type=accreditation_to_attest,
            )

            add_permission = Permission.objects.get(
                codename="add_accreditationtoattest",
                content_type=accreditation_to_attest,
            )
            change_permission = Permission.objects.get(
                codename="change_accreditationtoattest",
                content_type=accreditation_to_attest,
            )
            delete_permission = Permission.objects.get(
                codename="delete_accreditationtoattest",
                content_type=accreditation_to_attest,
            )

            # admins.permissions.add(
            #     view_permission, add_permission, change_permission, delete_permission
            # )
            # admins.save()

            # AccreditationToAccredit
            accreditation_to_accredit = ContentType.objects.get(
                app_label=AccreditationToAccredit._meta.app_label,
                model=AccreditationToAccredit._meta.object_name.lower(),
            )

            view_permission = Permission.objects.get(
                codename="view_accreditationtoaccredit",
                content_type=accreditation_to_accredit,
            )
            add_permission = Permission.objects.get(
                codename="add_accreditationtoaccredit",
                content_type=accreditation_to_accredit,
            )
            change_permission = Permission.objects.get(
                codename="change_accreditationtoaccredit",
                content_type=accreditation_to_accredit,
            )
            delete_permission = Permission.objects.get(
                codename="delete_accreditationtoaccredit",
                content_type=accreditation_to_accredit,
            )

            # AccreditationToOnboard
            accreditation_to_onboard = ContentType.objects.get(
                app_label=AccreditationToOnboard._meta.app_label,
                model=AccreditationToOnboard._meta.object_name.lower(),
            )

            view_permission = Permission.objects.get(
                codename="view_accreditationtoonboard",
                content_type=accreditation_to_onboard,
            )

            add_permission = Permission.objects.get(
                codename="add_accreditationtoonboard",
                content_type=accreditation_to_onboard,
            )
            change_permission = Permission.objects.get(
                codename="change_accreditationtoonboard",
                content_type=accreditation_to_onboard,
            )
            delete_permission = Permission.objects.get(
                codename="delete_accreditationtoonboard",
                content_type=accreditation_to_onboard,
            )

            # admins.permissions.add(
            #     view_permission, add_permission, change_permission, delete_permission
            # )
            # admins.save()

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

            print("Creating Holder permissions.")

            # Request VC
            request_vc_permission, _ = Permission.objects.get_or_create(
                codename="request_vc",
                name="Can request Verifiable Credentials",
                content_type=users_perm,
            )
            admins.permissions.add(request_vc_permission)
            admins.save()

            print("Success.")
        except Exception as e:
            print("Operation failed because: " + str(e))
