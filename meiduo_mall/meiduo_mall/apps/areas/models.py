from django.db import models

# Create your models here.


class Area(models.Model):
    """
    行政区划
    """
    name = models.CharField(max_length=20, verbose_name='名称')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True, verbose_name='上级行政区划')

    # django 默认每个主表的对象都有一个是外键的属性，可以通过它来查询到所有属于主表的子表的信息。 这个属性的名称默认是以子表的名称小写加上_set()来表示, 可以使用related_name来自定义
    # 主表：'self' area，子表: area, 子表在主表中对应的外键属性：related_name

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = '行政区划'

    def __str__(self):
        return self.name
