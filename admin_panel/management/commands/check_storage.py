"""Lista los buckets de Supabase Storage y valida los configurados en settings."""
from django.conf import settings
from django.core.management.base import BaseCommand
import supabase


class Command(BaseCommand):
    help = "Verifica (u opcionalmente crea) los buckets usados por productos y comprobantes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--create",
            action="store_true",
            help="Intenta crear los buckets faltantes como públicos.",
        )

    def handle(self, *args, **options):
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            self.stdout.write("SUPABASE_URL o SUPABASE_KEY no configurados.")
            return

        client = supabase.create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        try:
            buckets = client.storage.list_buckets()
        except Exception as exc:
            self.stderr.write(f"No se pudieron listar los buckets: {exc}")
            return

        names = [getattr(bucket, "name", str(bucket)) for bucket in buckets]
        self.stdout.write("Buckets disponibles en Supabase Storage:")
        for name in names:
            self.stdout.write(f"  - {name}")

        for label, expected in (
            ("Productos", settings.SUPABASE_STORAGE_BUCKET),
            ("Comprobantes", settings.SUPABASE_RECEIPTS_BUCKET),
        ):
            if expected in names:
                self.stdout.write(f"{label}: '{expected}' -> OK")
                continue

            self.stdout.write(f"{label}: '{expected}' -> FALTA")
            if options["create"]:
                try:
                    client.storage.create_bucket(
                        id=expected,
                        name=expected,
                        options={"public": True},
                    )
                    self.stdout.write(f"  Creado bucket público '{expected}'.")
                except Exception as exc:
                    self.stderr.write(
                        f"  No se pudo crear '{expected}': {exc}. "
                        "Crealo desde Supabase > Storage > Buckets o usá una service_role key."
                    )
