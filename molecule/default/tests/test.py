import os
import time
import pytest
import testinfra.utils.ansible_runner

# Conectează testinfra la inventory-ul Molecule
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


@pytest.mark.package
def test_nginx_package_installed(host):
    pkg = host.package("nginx")
    assert pkg.is_installed, "Nginx package should be installed"


@pytest.mark.service
def test_nginx_service_running_and_enabled(host):
    svc = host.service("nginx")
    assert svc.is_running, "Nginx service should be running"
    assert svc.is_enabled, "Nginx service should be enabled"


@pytest.mark.port
def test_port_80_listening(host):
    sock = host.socket("tcp://0.0.0.0:80")
    # Unele imagini pornesc cu un mic delay; așteptăm puțin
    for _ in range(10):
        if sock.is_listening:
            break
        time.sleep(1)
    assert sock.is_listening, "Port 80 should be listening on 0.0.0.0:80"


@pytest.mark.config
def test_nginx_config_syntax_ok(host):
    cmd = host.run("nginx -t")
    assert cmd.rc == 0, f"`nginx -t` failed: {cmd.stderr or cmd.stdout}"


@pytest.mark.http
def test_default_page_returns_200(host):
    # Folosim 127.0.0.1 ca să evităm DNS/hosts
    # curl -f returnează exit code != 0 dacă status != 200..299
    cmd = host.run("curl -fsS -o /dev/null -w '%%{http_code}' http://127.0.0.1/")
    assert cmd.rc == 0, f"curl failed: {cmd.stderr}"
    assert cmd.stdout.strip() == "200", f"Expected HTTP 200, got {cmd.stdout!r}"

    # opțional: conținutul ar trebui să menționeze nginx
    body = host.check_output("curl -fsS http://127.0.0.1/")
    assert "nginx" in body.lower(), "Landing page should mention 'nginx'"
