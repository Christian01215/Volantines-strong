"""Validaciones de RUT y de retiro usadas por el checkout."""
from datetime import timedelta

from django.test import SimpleTestCase
from django.utils import timezone

from config.validators import validate_pickup_data, validate_rut


class RutValidationTests(SimpleTestCase):
    def test_accepts_verifiers_one_and_k(self):
        valid_ruts = (
            "123456041",
            "12.345.604-1",
            "12345605K",
            "12.345.605-k",
            "12345670K",
            "12.345.678-5",
        )
        for rut in valid_ruts:
            with self.subTest(rut=rut):
                self.assertTrue(validate_rut(rut))

    def test_rejects_wrong_verifier(self):
        for rut in ("12.345.604-K", "12.345.605-1", "12.345.678-4", "12345678"):
            with self.subTest(rut=rut):
                self.assertFalse(validate_rut(rut))


class PickupValidationTests(SimpleTestCase):
    def test_requires_date_and_slot(self):
        errors = validate_pickup_data({})
        self.assertIn("Debe elegir una fecha de retiro.", errors)
        self.assertIn("Debe elegir un bloque horario de retiro.", errors)

    def test_accepts_future_date_and_known_slot(self):
        pickup_date = timezone.localdate() + timedelta(days=3)
        self.assertEqual(
            validate_pickup_data({
                "pickup_date": pickup_date.isoformat(),
                "pickup_slot": "10:00 - 12:00",
            }),
            [],
        )

    def test_rejects_past_date(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        errors = validate_pickup_data({
            "pickup_date": yesterday.isoformat(),
            "pickup_slot": "10:00 - 12:00",
        })
        self.assertIn("La fecha de retiro no puede ser anterior a hoy.", errors)

    def test_rejects_malformed_date_and_unknown_slot(self):
        errors = validate_pickup_data({
            "pickup_date": "no-es-una-fecha",
            "pickup_slot": "23:00 - 00:00",
        })
        self.assertIn("La fecha de retiro no es válida.", errors)
        self.assertIn("El bloque horario de retiro no es válido.", errors)
