from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post
from django.urls import reverse

User = get_user_model()


class StaticURLTests(TestCase):
    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, 200)


class PostURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        Post.objects.create(
            text='Тестовый текст',
            author=self.user
        )
        Group.objects.create(
            title='Тестовая группа',
            slug='test_group'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug': 'test_group'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'HasNoName'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': '1'}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': '1'}): 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_unexisting_url(self):
        response = self.authorized_client.get('/testtest')
        self.assertEqual(
            response.status_code, 404,
            'unexisting_url не работает')

    def test_rights_edit(self):
        response = self.guest_client.get(reverse('posts:post_edit',
                                         kwargs={'post_id': '1'}))
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id': '1'}))
        response_author = self.authorized_client.get(reverse('posts:post_edit',
                                                     kwargs={'post_id': '1'}))
        self.assertEqual(response_author.status_code, 200,
                         'автор не может редактировать свой пост')

    def test_rights_create(self):
        response = self.guest_client.get(reverse('posts:post_create'))
        self.assertRedirects(response, '/auth/login/?next=/create/')
        response_auth = self.authorized_client.get(
            reverse('posts:post_create'))
        self.assertEqual(response_auth.status_code, 200,
                         'активный пользователь не может создать пост')
