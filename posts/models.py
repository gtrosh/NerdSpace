from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название группы',
                             help_text='Дайте название группе',)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    class Meta:
        ordering = ['-pub_date']

    text = models.TextField(verbose_name='Текст поста',
                            help_text='Напишите текст поста')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts',
                               blank=True, null=True)
    group = models.ForeignKey(Group, verbose_name='Группа',
                              help_text='Выберите группу',
                              on_delete=models.SET_NULL,
                              related_name='posts',
                              blank=True, null=True)
    image = models.ImageField(upload_to='posts/', verbose_name='Картинка',
                              help_text='Добавьте картинку', blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='blog_posts')

    def __str__(self):
        return self.text[:15]

    def total_likes(self):
        return self.likes.count()


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True, null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True, null=True
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Напишите текст комментария',
    )
    created = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower', blank=True, null=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following', blank=True, null=True)
