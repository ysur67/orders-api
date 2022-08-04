# Generated by Django 4.0.7 on 2022-08-04 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationsReceiver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.CharField(max_length=300, verbose_name="ИД из telegram'а")),
                ('name', models.CharField(blank=True, max_length=300, null=True, verbose_name='Имя пользователя')),
            ],
            options={
                'verbose_name': 'Получатель сообщений',
                'verbose_name_plural': 'Получатели сообщений',
            },
        ),
    ]
