# Generated by Django 3.0.5 on 2020-04-23 18:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogapp', '0004_bookinstance_borrower'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookinstance',
            options={'ordering': ['due_back'], 'permissions': (('can_mark_returned', 'Set book as returned'),)},
        ),
    ]
