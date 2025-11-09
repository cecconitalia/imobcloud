# app_financeiro/migrations/000X_create_default_repasse_category.py
# (Use o número de migração correto, e.g., 0004, 0005, etc.)

from django.db import migrations

def create_default_repasse_category(apps, schema_editor):
    """
    Cria a Categoria 'Repasse de Aluguel' (Tipo: DESPESA) para todas as imobiliárias.
    """
    Categoria = apps.get_model('app_financeiro', 'Categoria')
    Imobiliaria = apps.get_model('core', 'Imobiliaria')
    
    NOME_CATEGORIA = 'Repasse de Aluguel'
    TIPO_CATEGORIA = 'DESPESA'

    # Itera sobre todas as imobiliárias para garantir que a categoria exista para cada tenant
    for imobiliaria in Imobiliaria.objects.all():
        Categoria.objects.get_or_create(
            imobiliaria=imobiliaria,
            nome=NOME_CATEGORIA,
            tipo=TIPO_CATEGORIA
        )

def reverse_default_repasse_category(apps, schema_editor):
    """
    Remove a categoria 'Repasse de Aluguel' no rollback.
    """
    Categoria = apps.get_model('app_financeiro', 'Categoria')
    
    # Remove todas as categorias com esse nome
    Categoria.objects.filter(nome='Repasse de Aluguel', tipo='DESPESA').delete()


class Migration(migrations.Migration):

    dependencies = [
        # O nome da dependência deve ser a última migração de app_financeiro
        # Se sua última migração foi 0003_... você deve usar '0003_...' aqui.
        ('app_financeiro', '0003_remove_transacao_conta_bancaria_and_more'), 
        ('core', '0001_initial'), # Dependência básica para a model Imobiliaria
    ]

    operations = [
        migrations.RunPython(create_default_repasse_category, reverse_default_repasse_category),
    ]