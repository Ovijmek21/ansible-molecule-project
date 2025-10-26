import os
import pytest
import testinfra.utils.ansible_runner

# This line connects testinfra to Molecule's Ansible-managed instance
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_nginx_package_installed(host):
    """Check that Nginx is installed."""
    nginx = host.package("nginx")
    assert nginx.is_installed, "Nginx package should be installed"


def test_nginx_service_running_and_enabled(host):
    """Check that Nginx service is running and enabled."""
    service = host.service("nginx")
    assert service.is_running, "Nginx service should be running"
    assert service.is_enabled, "Nginx service should be enabled"
