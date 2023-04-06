from django.db import models


# 改变模型需要这三步：
# 编辑 models.py 文件，改变模型。
# 运行 python manage.py makemigrations 为模型的改变生成迁移文件。
# 运行 python manage.py migrate 来应用数据库迁移。


class Content(models.Model):
    objects = None
    content_id = models.IntegerField(primary_key=True)
    title = models.TextField()
    banner = models.URLField()
    start_time = models.DateTimeField()
    content_text = models.TextField()

    def __str__(self):
        return self.title


class Update(models.Model):
    objects = None
    last_time = models.DateTimeField()
    last_total = models.IntegerField()
