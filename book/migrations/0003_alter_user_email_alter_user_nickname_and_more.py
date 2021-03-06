# Generated by Django 4.0.1 on 2022-01-24 05:10

import book.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0002_user_intro_user_nickname_user_profile_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.CharField(max_length=128, verbose_name='이메일'),
        ),
        migrations.AlterField(
            model_name='user',
            name='nickname',
            field=models.CharField(error_messages={'unique': '이미 사용중인 닉넥임입니다'}, max_length=15, null=True, unique=True, validators=[book.validators.validate_no_special_characters], verbose_name='별명'),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=65, verbose_name='비밀번호'),
        ),
    ]
