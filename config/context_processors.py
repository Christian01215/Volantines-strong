"""Datos del negocio disponibles en todas las plantillas."""
from django.conf import settings


def business(request):
    whatsapp = (settings.WHATSAPP_NUMBER or '').strip()
    digits = ''.join(char for char in whatsapp if char.isdigit())
    return {
        'whatsapp_number': whatsapp,
        'whatsapp_url': f'https://wa.me/{digits}' if digits else '#',
        'business_address': settings.BUSINESS_ADDRESS,
        'bank_name': settings.BANK_NAME,
        'bank_account_type': settings.BANK_ACCOUNT_TYPE,
        'bank_rut': settings.BANK_RUT,
        'bank_account': settings.BANK_ACCOUNT,
    }
