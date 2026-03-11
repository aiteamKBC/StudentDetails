import ipaddress
import errno
import os
import ssl
import socketserver
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from django.core.management.base import CommandError
from django.core.management.commands.runserver import Command as DjangoRunserverCommand
from django.core.servers import basehttp
from django.core.servers.basehttp import WSGIRequestHandler, WSGIServer
from django.utils import autoreload


def _ensure_dev_cert(cert_path: Path, key_path: Path) -> None:
    if cert_path.exists() and key_path.exists():
        return

    cert_path.parent.mkdir(parents=True, exist_ok=True)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "EG"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Local Dev"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ]
    )

    now = datetime.now(UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=3650))
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    x509.DNSName("localhost"),
                    x509.DNSName("127.0.0.1"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                ]
            ),
            critical=False,
        )
        .sign(private_key=key, algorithm=hashes.SHA256())
    )

    key_bytes = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    cert_bytes = cert.public_bytes(serialization.Encoding.PEM)

    key_path.write_bytes(key_bytes)
    cert_path.write_bytes(cert_bytes)


class SSLWSGIServer(WSGIServer):
    certfile = ""
    keyfile = ""

    def __init__(self, *args, **kwargs):
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.ssl_context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
        super().__init__(*args, **kwargs)

    def get_request(self):
        sock, addr = super().get_request()
        return self.ssl_context.wrap_socket(sock, server_side=True), addr


class SSLWSGIRequestHandler(WSGIRequestHandler):
    def get_environ(self):
        environ = super().get_environ()
        environ["HTTPS"] = "on"
        environ["wsgi.url_scheme"] = "https"
        return environ


def run_with_handler(
    addr,
    port,
    wsgi_handler,
    *,
    ipv6=False,
    threading=False,
    on_bind=None,
    server_cls=WSGIServer,
    request_handler_cls=WSGIRequestHandler,
):
    server_address = (addr, port)
    if threading:
        httpd_cls = type("WSGIServer", (socketserver.ThreadingMixIn, server_cls), {})
    else:
        httpd_cls = server_cls
    httpd = httpd_cls(server_address, request_handler_cls, ipv6=ipv6)
    if on_bind is not None:
        on_bind(getattr(httpd, "server_port", port))
    if threading:
        httpd.daemon_threads = True
    httpd.set_app(wsgi_handler)
    httpd.serve_forever()


class Command(DjangoRunserverCommand):
    help = "Starts a local HTTPS development server."
    protocol = "https"
    server_cls = SSLWSGIServer

    def run(self, **options):
        base_dir = Path(__file__).resolve().parents[4]
        cert_dir = base_dir / ".certs"
        cert_path = cert_dir / "localhost.pem"
        key_path = cert_dir / "localhost-key.pem"
        _ensure_dev_cert(cert_path, key_path)

        self.server_cls.certfile = str(cert_path)
        self.server_cls.keyfile = str(key_path)
        os.environ.setdefault("DJANGO_RUNSERVER_HIDE_WARNING", "true")
        super().run(**options)

    def inner_run(self, *args, **options):
        from django.db import connections

        autoreload.raise_last_exception()
        threading = options["use_threading"]
        shutdown_message = options.get("shutdown_message", "")

        if not options["skip_checks"]:
            self.stdout.write("Performing system checks...\n\n")
            check_kwargs = super().get_check_kwargs(options)
            check_kwargs["display_num_errors"] = True
            self.check(**check_kwargs)
        self.check_migrations()
        for conn in connections.all(initialized_only=True):
            conn.close()

        try:
            handler = self.get_handler(*args, **options)
            run_with_handler(
                self.addr,
                int(self.port),
                handler,
                ipv6=self.use_ipv6,
                threading=threading,
                on_bind=self.on_bind,
                server_cls=self.server_cls,
                request_handler_cls=SSLWSGIRequestHandler,
            )
        except OSError as e:
            errors = {
                errno.EACCES: "You don't have permission to access that port.",
                errno.EADDRINUSE: "That port is already in use.",
                errno.EADDRNOTAVAIL: "That IP address can't be assigned to.",
            }
            raise CommandError(errors.get(e.errno, e))
        except KeyboardInterrupt:
            if shutdown_message:
                self.stdout.write(shutdown_message)
