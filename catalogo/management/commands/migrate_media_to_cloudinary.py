from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
from catalogo.models import Trabajo, Documento
import os


class Command(BaseCommand):
    help = "Migrate existing local media files to Cloudinary storage"

    def handle(self, *args, **options):
        if not settings.USE_CLOUDINARY:
            self.stdout.write(self.style.ERROR("CLOUDINARY is not enabled. Aborting."))
            return

        self.stdout.write(self.style.SUCCESS("Starting migration to Cloudinary...\n"))

        # ---- Trabajo images ----
        for trabajo in Trabajo.objects.exclude(image=""):
            field = trabajo.image
            if not field:
                continue

            file_path = os.path.join(settings.MEDIA_ROOT, field.name)

            if not os.path.exists(file_path):
                self.stdout.write(f"[SKIP] File not found: {field.name}")
                continue

            with open(file_path, "rb") as f:
                field.save(field.name, File(f), save=True)

            self.stdout.write(f"[OK] Uploaded image: {field.name}")

        # ---- Documento files ----
        for doc in Documento.objects.exclude(file=""):
            field = doc.file
            if not field:
                continue

            file_path = os.path.join(settings.MEDIA_ROOT, field.name)

            if not os.path.exists(file_path):
                self.stdout.write(f"[SKIP] File not found: {field.name}")
                continue

            with open(file_path, "rb") as f:
                field.save(field.name, File(f), save=True)

            self.stdout.write(f"[OK] Uploaded document: {field.name}")

        self.stdout.write(self.style.SUCCESS("\nMigration completed."))
