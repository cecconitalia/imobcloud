# app_clientes/migrations/0008_...py (VERSÃO FINAL E CORRETA)
from django.db import migrations, models
import django.db.models.deletion

def criar_etapas_e_associar_clientes(apps, schema_editor):
    Imobiliaria = apps.get_model('core', 'Imobiliaria')
    EtapaFunil = apps.get_model('app_clientes', 'EtapaFunil')
    Cliente = apps.get_model('app_clientes', 'Cliente')
    etapas_padrao = ['Lead', 'Contato', 'Visita Agendada', 'Proposta', 'Negociação']

    for imobiliaria in Imobiliaria.objects.all():
        for nome_etapa in etapas_padrao:
            EtapaFunil.objects.get_or_create(imobiliaria=imobiliaria, nome=nome_etapa)
        etapa_lead = EtapaFunil.objects.get(imobiliaria=imobiliaria, nome='Lead')
        Cliente.objects.filter(imobiliaria=imobiliaria).update(etapa_funil=etapa_lead)

class Migration(migrations.Migration):
    dependencies = [
    ('app_clientes', '0007_alter_tarefa_options_alter_visita_options_etapafunil_and_more'),
    ('core', '0009_alter_imobiliaria_options_and_more'), # <--- LINHA CORRIGIDA
]
    operations = [
        # Deixe as operações que o Django gerou, exceto as relacionadas ao EtapaFunil

        # Nosso processo manual:
        migrations.CreateModel(
            name='EtapaFunil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50)),
                ('imobiliaria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.imobiliaria')),
            ],
            options={'unique_together': {('imobiliaria', 'nome')}},
        ),
        migrations.AddField(
            model_name='cliente',
            name='etapa_funil',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='app_clientes.etapafunil'),
        ),
        migrations.RunPython(criar_etapas_e_associar_clientes),
        migrations.AlterField(
            model_name='cliente',
            name='etapa_funil',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app_clientes.etapafunil'),
        ),
    ]