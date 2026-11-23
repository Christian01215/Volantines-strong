"""Prueba la configuración SMTP de Gmail y envía un correo de diagnóstico."""
import smtplib
import socket

from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Prueba la conexión SMTP y, opcionalmente, envía un correo de prueba. "
        "No imprime contraseñas."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--to",
            default=settings.ADMIN_EMAIL,
            help="Destinatario del correo de prueba (por defecto ADMIN_EMAIL).",
        )
        parser.add_argument(
            "--no-send",
            action="store_true",
            help="Solo prueba conexión y autenticación, sin enviar correo.",
        )

    def handle(self, *args, **options):
        recipient = (options["to"] or "").strip()
        self.stdout.write("Configuración de correo:")
        self.stdout.write(f"  Backend: {settings.EMAIL_BACKEND}")
        self.stdout.write(
            f"  Servidor: {settings.EMAIL_HOST}:{settings.EMAIL_PORT} "
            f"(TLS={settings.EMAIL_USE_TLS}, SSL={settings.EMAIL_USE_SSL})"
        )
        self.stdout.write(f"  Usuario: {settings.EMAIL_HOST_USER or '(vacío)'}")
        self.stdout.write(
            "  Contraseña: "
            f"{'configurada' if settings.EMAIL_HOST_PASSWORD else 'FALTA'}"
        )
        self.stdout.write(f"  Remitente: {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"  Destinatario: {recipient or '(vacío)'}")

        if "smtp" not in settings.EMAIL_BACKEND:
            self.stderr.write(
                "El backend actual no es SMTP. Define "
                "EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend."
            )
            return

        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            self.stderr.write(
                "Faltan EMAIL_HOST_USER o EMAIL_HOST_PASSWORD en el entorno."
            )
            return

        connection = get_connection()
        try:
            try:
                connection.open()
            except smtplib.SMTPAuthenticationError as exc:
                self.stderr.write(
                    self.style.ERROR("Gmail rechazó el usuario o la contraseña.")
                )
                self.stderr.write(
                    "Revisa que EMAIL_HOST_USER sea una cuenta de Google completa "
                    "(Gmail o Google Workspace), que EMAIL_HOST_PASSWORD sea una "
                    "contraseña de aplicación de 16 caracteres sin espacios y que "
                    "la verificación en dos pasos esté activa."
                )
                self.stderr.write(f"Detalle: {exc}")
                return
            except (
                smtplib.SMTPConnectError,
                smtplib.SMTPServerDisconnected,
                socket.timeout,
                TimeoutError,
                OSError,
            ) as exc:
                self.stderr.write(
                    self.style.ERROR(
                        f"No se pudo conectar a "
                        f"{settings.EMAIL_HOST}:{settings.EMAIL_PORT}."
                    )
                )
                self.stderr.write(
                    "Si el puerto 587 está bloqueado, prueba EMAIL_PORT=465, "
                    "EMAIL_USE_SSL=True y EMAIL_USE_TLS=False."
                )
                self.stderr.write(f"Detalle: {exc}")
                return

            self.stdout.write(
                self.style.SUCCESS("Conexión y autenticación SMTP: OK")
            )

            if options["no_send"]:
                self.stdout.write("No se envió correo (--no-send).")
                return

            if not recipient:
                self.stderr.write(
                    "No hay destinatario. Usa --to o define ADMIN_EMAIL."
                )
                return

            message = EmailMessage(
                subject="Prueba de correo — Volantines Strong",
                body=(
                    "Este es un correo de prueba enviado desde Volantines Strong.\n\n"
                    f"Backend: {settings.EMAIL_BACKEND}\n"
                    f"Remitente: {settings.DEFAULT_FROM_EMAIL}\n"
                    f"Servidor: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
            )

            try:
                sent = connection.send_messages([message])
            except smtplib.SMTPSenderRefused as exc:
                self.stderr.write(
                    self.style.ERROR(
                        "Gmail rechazó el remitente configurado en "
                        "DEFAULT_FROM_EMAIL."
                    )
                )
                self.stderr.write(
                    "Usa la misma cuenta de EMAIL_HOST_USER como remitente o "
                    "configura un alias verificado en Gmail > Enviar como."
                )
                self.stderr.write(f"Detalle: {exc}")
                return
            except smtplib.SMTPRecipientsRefused as exc:
                self.stderr.write(
                    self.style.ERROR(
                        f"Gmail rechazó el destinatario {recipient}."
                    )
                )
                self.stderr.write(f"Detalle: {exc}")
                return
            except Exception as exc:
                self.stderr.write(
                    self.style.ERROR(f"No se pudo enviar el correo: {exc}")
                )
                return

            if sent:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Correo de prueba enviado a {recipient}."
                    )
                )
            else:
                self.stderr.write("El correo de prueba no se envió.")
        finally:
            connection.close()
