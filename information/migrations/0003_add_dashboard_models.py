# Generated manually for new dashboard models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('information', '0002_alter_project_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectInquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(max_length=100)),
                ('client_email', models.EmailField(max_length=254)),
                ('client_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('project_title', models.CharField(max_length=200)),
                ('project_description', models.TextField()),
                ('project_type', models.CharField(choices=[('web-app', 'Web Application'), ('mobile-app', 'Mobile Application'), ('e-commerce', 'E-commerce'), ('desktop-app', 'Desktop Application'), ('other', 'Other')], default='web-app', max_length=20)),
                ('budget', models.CharField(max_length=100)),
                ('timeline', models.CharField(max_length=100)),
                ('additional_requirements', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in-progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=10)),
                ('estimated_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('actual_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('progress', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='InquiryMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(choices=[('client', 'Client'), ('admin', 'Admin')], max_length=10)),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('inquiry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='information.projectinquiry')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in-progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('assigned_to', models.CharField(default='admin', max_length=50)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('inquiry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='information.projectinquiry')),
            ],
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('role', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('inquiry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_members', to='information.projectinquiry')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('type', models.CharField(choices=[('info', 'Info'), ('success', 'Success'), ('warning', 'Warning'), ('error', 'Error')], default='info', max_length=10)),
                ('category', models.CharField(choices=[('inquiry', 'Inquiry'), ('task', 'Task'), ('document', 'Document'), ('invoice', 'Invoice'), ('general', 'General')], default='general', max_length=20)),
                ('is_read', models.BooleanField(default=False)),
                ('action_url', models.URLField(blank=True, null=True)),
                ('action_text', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('quantity', models.IntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='information.invoice')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(max_length=50, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('sent', 'Sent'), ('paid', 'Paid'), ('overdue', 'Overdue'), ('cancelled', 'Cancelled')], default='sent', max_length=20)),
                ('due_date', models.DateTimeField()),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('inquiry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='information.projectinquiry')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('type', models.CharField(choices=[('contract', 'Contract'), ('nda', 'NDA'), ('agreement', 'Agreement'), ('proposal', 'Proposal'), ('other', 'Other')], max_length=20)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('pending-signature', 'Pending Signature'), ('signed', 'Signed'), ('expired', 'Expired')], default='draft', max_length=20)),
                ('download_url', models.URLField()),
                ('signed_at', models.DateTimeField(blank=True, null=True)),
                ('signed_by', models.CharField(blank=True, max_length=100, null=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('inquiry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='information.projectinquiry')),
            ],
        ),
    ]
