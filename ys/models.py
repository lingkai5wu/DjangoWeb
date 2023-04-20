from django.db import models
from django.utils import timezone


# 改变模型需要这三步：
# 编辑 models.py 文件，改变模型。
# 运行 python manage.py makemigrations 为模型的改变生成迁移文件。
# 运行 python manage.py migrate 来应用数据库迁移。


class Content(models.Model):
    content_id = models.IntegerField(primary_key=True)
    title = models.TextField()
    banner = models.URLField()
    start_time = models.DateTimeField()
    content_text = models.TextField()

    def __str__(self):
        return self.title


class Update(models.Model):
    update_time = models.DateTimeField()
    total = models.IntegerField()

    def get_update_time_diff(self):
        now = timezone.now()
        diff = now - self.update_time
        total_seconds = diff.total_seconds()

        if total_seconds < 60:
            return str(int(total_seconds)) + "秒"
        elif total_seconds < 3600:
            return str(int(total_seconds / 60)) + "分钟"
        elif total_seconds < 86400:
            return str(int(total_seconds / 3600)) + "小时"
        else:
            return str(int(total_seconds / 86400)) + "天"
