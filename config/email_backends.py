"""Backend de correo para Django usando la API HTTP de Resend."""
import base64

import httpx
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend


class ResendEmailBackend(BaseEmailBackend):
    """Envía EmailMessage/EmailMultiAlternatives a través de Resend.

    Resend espera los adjuntos como base64 en el campo ``content``.
    No depende del SDK oficial: usa httpx, que ya está instalado con Supabase.
    """

    API_URL = "https://api.resend.com/emails"

    def __init__(self, api_key=None, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.api_key = api_key or getattr(settings, "RESEND_API_KEY", "")
        self.timeout = getattr(settings, "RESEND_TIMEOUT", 15)

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        if not self.api_key:
            if not self.fail_silently:
                raise ImproperlyConfigured("RESEND_API_KEY no está definida en el entorno")
            return 0

        sent = 0
        for message in email_messages:
            if self._send(message):
                sent += 1
        return sent

    def _send(self, message):
        html_body = None
        for content, mimetype in message.alternatives:
            if mimetype == "text/html":
                html_body = content
                break

        payload = {
            "from": message.from_email or settings.DEFAULT_FROM_EMAIL,
            "to": list(message.to),
            "subject": message.subject,
        }
        if message.cc:
            payload["cc"] = list(message.cc)
        if message.bcc:
            payload["bcc"] = list(message.bcc)
        if html_body:
            payload["html"] = html_body
            if message.body:
                payload["text"] = message.body
        else:
            payload["text"] = message.body or ""

        attachments = []
        for filename, content, _mimetype in message.attachments:
            if isinstance(content, str):
                content = content.encode("utf-8")
            attachments.append({
                "filename": filename,
                "content": base64.b64encode(content).decode("ascii"),
            })
        if attachments:
            payload["attachments"] = attachments

        try:
            response = httpx.post(
                self.API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return True
        except Exception:
            if not self.fail_silently:
                raise
            return False
