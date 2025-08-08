# core/migrations/0009_...py (VERSÃO FINAL E CORRETA)
from django.db import migrations, models
import django.db.models.deletion

def popular_imobiliaria_em_notificacoes_antigas(apps, schema_editor):
    Notificacao = apps.get_model('core', 'Notificacao')
    Imobiliaria = apps.get_model('core', 'Imobiliaria')
    imobiliaria_padrao = Imobiliaria.objects.order_by('pk').first()
    if imobiliaria_padrao:
        Notificacao.objects.filter(imobiliaria__isnull=True).update(imobiliaria=imobiliaria_padrao)
    else: # Se não houver imobiliárias, apaga as notificações órfãs
        Notificacao.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0008_notificacao'),
    ]
    operations = [
        # Adicione aqui as operações que o Django gerou, exceto o AddField e AlterField de 'imobiliaria'
        # Se o Django gerou: migrations.AddField(model_name='notificacao', ...), APAGUE ESSA LINHA.

        # Nosso processo manual e seguro:
        migrations.AddField(
            model_name='notificacao',
            name='imobiliaria',
            field=models.ForeignKey(null=True, to='core.imobiliaria', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.RunPython(popular_imobiliaria_em_notificacoes_antigas),
        migrations.AlterField(
            model_name='notificacao',
            name='imobiliaria',
            field=models.ForeignKey(to='core.imobiliaria', on_delete=django.db.models.deletion.CASCADE),
        ),
    ]