from django.core.management.base import BaseCommand
from django.db import connection
from properties.models import Property

class Command(BaseCommand):
    help = 'Conta registros da tabela Property em schema tenant'

    def add_arguments(self, parser):
        parser.add_argument('schema', type=str, help='Nome do schema tenant')

    def handle(self, *args, **options):
        schema = options['schema']
        connection.set_schema(schema)
        count = Property.objects.count()
        self.stdout.write(f'No schema "{schema}" existem {count} propriedades.')
