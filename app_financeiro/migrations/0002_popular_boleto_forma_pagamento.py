from django.db import migrations

def popular_boleto(apps, schema_editor):
    Imobiliaria = apps.get_model('core', 'Imobiliaria')
    FormaPagamento = apps.get_model('app_financeiro', 'FormaPagamento')

    for imobiliaria in Imobiliaria.objects.all():
        FormaPagamento.objects.update_or_create(
            imobiliaria=imobiliaria,
            nome='Boleto',
            defaults={'slug': 'boleto', 'ativo': True}
        )

class Migration(migrations.Migration):
    dependencies = [
        ('app_financeiro', '0001_initial'),
        ('core', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(popular_boleto),
    ]