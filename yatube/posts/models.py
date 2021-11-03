from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Модель сообществ в которые
       можно публиковать статьи"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        """Значение выводимое при печати"""
        return self.title


class Post(models.Model):
    """Модель статьи в блоге."""
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(Group,
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              related_name='posts',)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']


class Comment(models.Model):
    """Модель коментария в блоге."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='coments',)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='coments')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-created']


class Follow(models.Model):
    """Модель подписки на автора."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique follow')
        ]
