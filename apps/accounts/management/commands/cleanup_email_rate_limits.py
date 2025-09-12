from django.core.management.base import BaseCommand
from apps.accounts.models import EmailSendRateLimit

class Command(BaseCommand):
    help = '清理旧的邮箱发送频率限制记录'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='保留多少天内的记录（默认7天）',
        )

    def handle(self, *args, **options):
        days = options['days']
        
        deleted_count = EmailSendRateLimit.cleanup_old_records(days=days)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'成功清理了 {deleted_count} 条超过 {days} 天的发送记录'
            )
        )
