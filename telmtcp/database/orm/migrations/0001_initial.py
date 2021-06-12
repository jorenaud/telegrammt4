# Generated by Django 2.2.6 on 2021-02-22 16:11

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='tbl_alert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, max_length=255)),
                ('message', models.CharField(blank=True, max_length=255)),
                ('priority', models.CharField(blank=True, max_length=255)),
                ('status', models.IntegerField(blank=True, default=0)),
            ],
        ),
        migrations.CreateModel(
            name='tbl_blocked_ip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blocked', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='tbl_crypto_order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(default=0)),
                ('crypto', models.CharField(blank=True, max_length=20)),
                ('address', models.CharField(blank=True, max_length=1255)),
                ('private', models.CharField(blank=True, max_length=1255)),
                ('plan_id', models.IntegerField(blank=True, default=0)),
                ('expire_date', models.DateTimeField(blank=True)),
                ('create_date', models.DateTimeField(blank=True)),
                ('custom_account_cn', models.IntegerField(blank=True, default=0)),
                ('amount', models.FloatField(blank=True, default=0)),
                ('received', models.FloatField(blank=True, default=0)),
                ('price', models.FloatField(blank=True, default=0)),
                ('custom_plan_type', models.CharField(blank=True, max_length=255)),
                ('affiliate', models.IntegerField(blank=True, default=0)),
                ('ex_price', models.FloatField(blank=True, default=0)),
                ('gas_price', models.FloatField(blank=True, default=0)),
                ('status', models.IntegerField(default=0)),
                ('order_id', models.CharField(blank=True, max_length=255)),
                ('txs', models.CharField(blank=True, max_length=1024)),
                ('refunded', models.FloatField(blank=True, default=0)),
                ('ref_code', models.IntegerField(blank=True, default=0)),
                ('ref_message', models.CharField(blank=True, max_length=255)),
                ('ref_tx', models.CharField(blank=True, max_length=255)),
                ('transferred', models.IntegerField(blank=True, default=0)),
            ],
        ),
        migrations.CreateModel(
            name='tbl_custom_plan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, max_length=255)),
                ('price', models.FloatField(blank=True, default=0)),
            ],
        ),
        migrations.CreateModel(
            name='tbl_demo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(blank=True, max_length=255)),
                ('register_date', models.DateTimeField(auto_now_add=True)),
                ('expire_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='tbl_ip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(blank=True, max_length=255)),
                ('type', models.CharField(blank=True, max_length=255)),
                ('register_date', models.DateTimeField(auto_now_add=True)),
                ('ip', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='tbl_order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userid', models.IntegerField(blank=True)),
                ('phone', models.CharField(blank=True, max_length=255)),
                ('email', models.CharField(blank=True, max_length=255)),
                ('account', models.CharField(blank=True, max_length=255)),
                ('plan_id', models.IntegerField(blank=True, default=0)),
                ('expire_date', models.DateTimeField(blank=True)),
                ('create_date', models.DateTimeField(blank=True)),
                ('subscription_id', models.CharField(blank=True, max_length=255)),
                ('custom_account_cn', models.IntegerField(blank=True, default=0)),
                ('subscription_deactived', models.IntegerField(blank=True, default=0)),
                ('price', models.FloatField(blank=True, default=0)),
                ('custom_plan_type', models.CharField(blank=True, max_length=255)),
                ('affiliate', models.IntegerField(blank=True, default=0)),
            ],
        ),
        migrations.CreateModel(
            name='tbl_patch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(blank=True, max_length=255)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('url', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='tbl_plan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('price', models.FloatField(blank=True, default=0)),
                ('period', models.CharField(blank=True, max_length=255)),
                ('account_count', models.IntegerField(blank=True, default=0)),
            ],
        ),
        migrations.CreateModel(
            name='tbl_promo_email',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(blank=True, max_length=255)),
                ('message', models.CharField(blank=True, max_length=1024)),
                ('sent', models.IntegerField(blank=True, default=0)),
            ],
        ),
        migrations.CreateModel(
            name='tbl_schema',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(blank=True, default=0)),
                ('expression', models.CharField(blank=True, max_length=2555)),
            ],
        ),
        migrations.CreateModel(
            name='tbl_user',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('s_password', models.CharField(default='', max_length=512)),
                ('phone', models.CharField(blank=True, max_length=255)),
                ('affiliate', models.IntegerField(blank=True, default=0)),
                ('eth_address', models.CharField(blank=True, max_length=1024)),
                ('eth_private', models.CharField(blank=True, max_length=1024)),
                ('eth_balance', models.FloatField(blank=True, default=0)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]