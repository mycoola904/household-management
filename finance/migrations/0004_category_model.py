from django.db import migrations, models
import django.db.models.deletion


def create_default_category(apps, schema_editor):
    Category = apps.get_model("finance", "Category")
    if not Category.objects.exists():
        Category.objects.create(name="General")


def purge_transactions(apps, schema_editor):
    Transaction = apps.get_model("finance", "Transaction")
    Transaction.objects.all().delete()


def assign_default_category(apps, schema_editor):
    Category = apps.get_model("finance", "Category")
    Transaction = apps.get_model("finance", "Transaction")
    default_category = Category.objects.order_by("pk").first()
    if default_category:
        Transaction.objects.filter(category__isnull=True).update(category=default_category)


class Migration(migrations.Migration):
    dependencies = [
        ("finance", "0003_transaction"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(editable=False, max_length=120, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.RunPython(create_default_category, migrations.RunPython.noop),
        migrations.RunPython(purge_transactions, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="transaction",
            name="category",
        ),
        migrations.AddField(
            model_name="transaction",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="transactions",
                to="finance.category",
            ),
        ),
        migrations.RunPython(assign_default_category, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="transaction",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="transactions",
                to="finance.category",
            ),
        ),
    ]
