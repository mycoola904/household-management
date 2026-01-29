from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Seed the database using the project's seed_data module."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run the seed code in a transaction and roll it back (if supported by your seed functions).",
        )

    def handle(self, *args, **options):
        # Import here (not at module import time) so Django loads cleanly even if seeds aren't ready.
        try:
            # Update this import path to match where you placed seed_data.py
            from seeds.seed_data import main as seed_main
        except Exception as exc:
            raise CommandError(
                "Could not import seed function. "
                "Update the import in core/management/commands/seed.py "
                "to point at your seed_data.py (expected seeds.seed_data.main)."
            ) from exc

        dry_run = options.get("dry_run", False)

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN: seeding will be rolled back."))
            try:
                with transaction.atomic():
                    seed_main()
                    # Force rollback by raising an exception inside the atomic block
                    raise RuntimeError("Dry run rollback")
            except RuntimeError as exc:
                if str(exc) == "Dry run rollback":
                    self.stdout.write(self.style.SUCCESS("Dry run complete (rolled back)."))
                    return
                raise
        else:
            self.stdout.write("Seeding database...")
            with transaction.atomic():
                seed_main()
            self.stdout.write(self.style.SUCCESS("Seeding complete."))
