# Generated migration for TestResult model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_user_test_results'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseditem',
            name='item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.item'),
        ),
        migrations.AddField(
            model_name='purchaseditem',
            name='amount_paid',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='purchaseditem',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterModelOptions(
            name='purchaseditem',
            options={'ordering': ['-purchased_at']},
        ),
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_name', models.CharField(max_length=255)),
                ('company', models.CharField(blank=True, max_length=50)),
                ('difficulty', models.CharField(blank=True, max_length=20)),
                ('total_questions', models.IntegerField()),
                ('correct_answers', models.IntegerField()),
                ('score', models.IntegerField()),
                ('time_taken', models.CharField(blank=True, max_length=20)),
                ('attempt_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_results_db', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-attempt_date'],
            },
        ),
    ]
