from django.db import migrations

def create_default_unidade(apps, schema_editor):
    Unidade = apps.get_model('core', 'Unidade')

    Unidade.objects.get_or_create(
        nome="Loja Lulu-Burguer",
        defaults={
            "endereco": "Av Chico Xavier 1010",
            "ativa": True
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_unidade),
    ]