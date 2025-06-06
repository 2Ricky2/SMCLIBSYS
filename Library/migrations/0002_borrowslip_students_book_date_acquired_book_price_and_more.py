# Generated by Django 5.1.7 on 2025-04-30 08:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Library', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BorrowSlip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Schedule', models.DateField()),
                ('ScheduleDue', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Students',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=255)),
                ('lastname', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255, unique=True)),
                ('password', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='book',
            name='Date_acquired',
            field=models.DateTimeField(default=None),
        ),
        migrations.AddField(
            model_name='book',
            name='price',
            field=models.IntegerField(default=None),
        ),
        migrations.CreateModel(
            name='BooksStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('BookStatus', models.BooleanField()),
                ('Book_id', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='Library.book')),
            ],
        ),
        migrations.CreateModel(
            name='Books_Borrowed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Book_id', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='Library.book')),
                ('BorrowSlip_id', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='Library.borrowslip')),
            ],
        ),
        migrations.CreateModel(
            name='Penalty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calculated_ammount', models.IntegerField()),
                ('BorrowSlip_id', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='Library.borrowslip')),
                ('Student_id', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='Library.students')),
            ],
        ),
        migrations.AddField(
            model_name='borrowslip',
            name='Student_id',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='Library.students'),
        ),
    ]
