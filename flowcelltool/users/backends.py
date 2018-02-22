from django_auth_ldap.backend import LDAPBackend, _LDAPUser
from django.conf import settings

# Username domains for primary and secondary LDAP backends
USERNAME_DOMAIN = settings.AUTH_LDAP_USERNAME_DOMAIN
USERNAME_DOMAIN2 = settings.AUTH_LDAP2_USERNAME_DOMAIN


# Primary LDAP backend
class PrimaryLDAPBackend(LDAPBackend):
    settings_prefix = 'AUTH_LDAP_'

    def authenticate(
            self, request=None, username=None, password=None, **kwargs):
        if (username.find('@') == -1 or
                username.split('@')[1].upper() != USERNAME_DOMAIN):
            return None
        ldap_user = _LDAPUser(self, username=username.split('@')[0].strip())
        user = ldap_user.authenticate(password)
        return user

    def ldap_to_django_username(self, username):
        """Override LDAPBackend function to get the username with domain"""
        return username + '@' + USERNAME_DOMAIN

    def django_to_ldap_username(self, username):
        """Override LDAPBackend function to get the real LDAP username"""
        return username.split('@')[0]


# Secondary AD backend
class SecondaryLDAPBackend(LDAPBackend):
    settings_prefix = 'AUTH_LDAP2_'

    def authenticate(
            self, request=None, username=None, password=None, **kwargs):
        if (username.find('@') == -1 or
                username.split('@')[1].upper() != USERNAME_DOMAIN2):
            return None
        ldap_user = _LDAPUser(self, username=username.split('@')[0].strip())
        user = ldap_user.authenticate(password)
        return user

    def ldap_to_django_username(self, username):
        """Override LDAPBackend function to get the username with domain"""
        return username + '@' + USERNAME_DOMAIN2

    def django_to_ldap_username(self, username):
        """Override LDAPBackend function to get the real LDAP username"""
        return username.split('@')[0]
