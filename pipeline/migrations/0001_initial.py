# Generated by Django 2.0.2 on 2018-06-05 14:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('component_browser', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('run_time', models.DateTimeField(blank=True, null=True)),
                ('output', models.TextField(blank=True, null=True)),
                ('output_time', models.DateTimeField(blank=True, null=True)),
                ('position', models.IntegerField()),
                ('local_id', models.IntegerField()),
                ('parameters', models.ManyToManyField(blank=True, related_name='has_params', to='component_browser.Parameter')),
            ],
        ),
        migrations.CreateModel(
            name='Pipeline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(max_length=200)),
                ('local_id_gen', models.IntegerField(default=0)),
                ('requests', models.ManyToManyField(blank=True, related_name='multiple', to='component_browser.PathRequest')),
            ],
        ),
        migrations.AddField(
            model_name='pipe',
            name='pipe_line',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pipeline.Pipeline'),
        ),
        migrations.AddField(
            model_name='pipe',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='component_browser.PathRequest'),
        ),
    ]
