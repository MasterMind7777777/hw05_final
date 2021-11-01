from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from posts.models import Post

from posts.models import Follow

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.usr_sub = User.objects.create_user(username='usr_sub')
        cls.usr_nonsub = User.objects.create_user(username='usr_nonsub')

    def setUp(self):
        self.authorized_client_sub = Client()
        self.authorized_client_nonsub = Client()
        self.authorized_client_sub.force_login(self.usr_sub)
        self.authorized_client_nonsub.force_login(self.usr_nonsub)
        Post.objects.create(
            text='Тестовый текст nonsub',
            author=self.usr_nonsub,
        )
        Post.objects.create(
            text='Тестовый текст sub',
            author=self.usr_sub,
        )

    def test_subscription(self):
        self.authorized_client_nonsub.get(
            reverse('posts:profile_follow', kwargs={'username': 'usr_sub'}))

        self.assertTrue(Follow.objects.filter(
            user=self.usr_nonsub, author=self.usr_sub
        ).exists)

    def test_only_subscriptions_on_subpage(self):
        self.authorized_client_sub.get(
            reverse('posts:profile_follow', kwargs={'username': 'usr_sub'}))

        follow_index_sub = self.authorized_client_sub.get(
            reverse('posts:follow_index')
        )
        follow_index_nonsub = self.authorized_client_nonsub.get(
            reverse('posts:follow_index')
        )

        self.assertIsNotNone(
            follow_index_sub, 'Ползователю не выводятся его подписки')
        self.assertIsNotNone(
            follow_index_nonsub,
            'Ползователю выводятся посты на которые он не подписан')
