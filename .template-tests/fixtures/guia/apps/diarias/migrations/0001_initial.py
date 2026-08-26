# Migração inicial escrita à mão, espelhando a estrutura gerada pelo Django
# para o app exemplo. Ela SHIPA junto com o app: quem segue o guia nunca
# roda makemigrations — a consistência com models.py é provada por
# `makemigrations diarias --check --dry-run` na suíte de ensaio.

import django.core.validators
import django.db.models.deletion
import simple_history.models
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalViagem',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('servidor', models.CharField(max_length=150, verbose_name='servidor')),
                ('destino', models.CharField(max_length=150, verbose_name='destino')),
                ('data_inicio', models.DateField(verbose_name='início')),
                ('data_fim', models.DateField(verbose_name='fim')),
                ('motivo', models.TextField(verbose_name='motivo')),
                ('valor_diarias', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='valor de diárias')),
                ('valor_passagens', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='valor de passagens')),
                ('status', models.CharField(choices=[('SOLICITADA', 'Solicitada'), ('APROVADA', 'Aprovada'), ('PAGA', 'Paga'), ('CANCELADA', 'Cancelada')], default='SOLICITADA', max_length=20, verbose_name='status')),
                ('criado_em', models.DateTimeField(blank=True, editable=False, verbose_name='criado em')),
                ('atualizado_em', models.DateTimeField(blank=True, editable=False, verbose_name='atualizado em')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical viagem',
                'verbose_name_plural': 'historical viagens',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Viagem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('servidor', models.CharField(max_length=150, verbose_name='servidor')),
                ('destino', models.CharField(max_length=150, verbose_name='destino')),
                ('data_inicio', models.DateField(verbose_name='início')),
                ('data_fim', models.DateField(verbose_name='fim')),
                ('motivo', models.TextField(verbose_name='motivo')),
                ('valor_diarias', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='valor de diárias')),
                ('valor_passagens', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='valor de passagens')),
                ('status', models.CharField(choices=[('SOLICITADA', 'Solicitada'), ('APROVADA', 'Aprovada'), ('PAGA', 'Paga'), ('CANCELADA', 'Cancelada')], default='SOLICITADA', max_length=20, verbose_name='status')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
            ],
            options={
                'verbose_name': 'viagem',
                'verbose_name_plural': 'viagens',
                'ordering': ['-criado_em'],
            },
        ),
    ]
