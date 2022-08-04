# Generated by Django 4.0.7 on 2022-08-04 08:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
        ('feedback', '0002_ordernotification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordernotification',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='orders.order', verbose_name='Заказ'),
        ),
        migrations.AlterField(
            model_name='ordernotification',
            name='receiver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='feedback.notificationsreceiver', verbose_name='Получатель сообщения'),
        ),
    ]
