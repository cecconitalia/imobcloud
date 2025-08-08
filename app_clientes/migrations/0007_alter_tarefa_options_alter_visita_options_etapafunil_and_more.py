# app_clientes/migrations/0007_...py (COLE ESTE CÓDIGO)

from django.db import migrations, models
import django.db.models.deletion

def criar_etapas_e_definir_padrao(apps, schema_editor):
    """
    Cria as Etapas do Funil e define um valor padrão para todos os Clientes existentes.
    """
    EtapaFunil = apps.get_model('app_clientes', 'EtapaFunil')
    Cliente = apps.get_model('app_clientes', 'Cliente')

    # Cria as etapas
    etapas = ['Lead', 'Contato', 'Visita Agendada', 'Proposta', 'Negociação']
    for nome_etapa in etapas:
        EtapaFunil.objects.get_or_create(nome=nome_etapa)

    # Define 'Lead' como padrão para todos os clientes existentes
    if Cliente.objects.exists():
        etapa_lead = EtapaFunil.objects.get(nome='Lead')
        Cliente.objects.update(etapa_funil=etapa_lead)


class Migration(migrations.Migration):

    dependencies = [
        ('app_clientes', '0006_alter_tarefa_oportunidade'),
    ]

    operations = [
        # ETAPA 1: Criar a tabela para as Etapas do Funil.
        migrations.CreateModel(
            name='EtapaFunil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
            ],
        ),

        # ETAPA 2: Adicionar o novo campo ForeignKey, permitindo valores nulos TEMPORARIAMENTE.
        migrations.AddField(
            model_name='cliente',
            name='etapa_funil',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='app_clientes.etapafunil'),
        ),

        # ETAPA 3: Rodar a função que cria as etapas E define o valor padrão para todos.
        migrations.RunPython(criar_etapas_e_definir_padrao),

        # ETAPA 4: Agora que todos os campos têm um valor, podemos tornar a coluna obrigatória.
        migrations.AlterField(
            model_name='cliente',
            name='etapa_funil',
            field=models.ForeignKey(null=False, on_delete=django.db.models.deletion.PROTECT, to='app_clientes.etapafunil'),
        ),

        # Outras alterações que o Django incluiu na migração original:
        migrations.AlterModelOptions(
            name='tarefa',
            options={'ordering': ['data_vencimento']},
        ),
        migrations.AlterModelOptions(
            name='visita',
            options={'ordering': ['data_hora']},
        ),
    ]