from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

User = get_user_model()


class PostPagesTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )

        Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            image=self.uploaded
        )
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group'
        )
        for i in range(1, 13):
            Post.objects.create(
                text='Тестовый текст',
                author=self.user,
                group=self.group,
                image=self.uploaded
            )

    def test_views_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug': 'test_group'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'StasBasov'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': 1}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': 1}): 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text

        response2 = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), 10, 'первая страница index')
        self.assertEqual(len(
            response2.context['page_obj']), 3, 'вторая страница index')

        self.assertEqual(post_text_0, 'Тестовый текст')

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_posts',
                    kwargs={'slug': 'test_group'}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group

        response2 = self.authorized_client.get(
            reverse('posts:group_posts',
                    kwargs={'slug': 'test_group'}) + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), 10, 'первая страница group_posts')
        self.assertEqual(len(
            response2.context['page_obj']), 2, 'вторая страница group_posts')

        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_group_0, self.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': 'StasBasov'}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_user_0 = first_object.author

        response2 = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': 'StasBasov'}) + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), 10, 'первая страница profile')
        self.assertEqual(len(
            response2.context['page_obj']), 3, 'вторая страница profile')

        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_user_0, self.user)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': 1}))
        first_object = response.context['post']
        post_text_0 = first_object.text

        self.assertEqual(post_text_0, 'Тестовый текст')

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': 1}))
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_added_correctly(self):
        """Пост при создании добавлен корректно"""
        post = Post.objects.create(
            text='Тестовый текст проверка как добавился',
            author=self.user,
            group=self.group
        )

        response_index = self.authorized_client.get(reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'test_group'}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'StasBasov'}))

        objects_index = response_index.context['page_obj']
        objects_group = response_group.context['page_obj']
        objects_profile = response_profile.context['page_obj']

        obj_i_in = False
        obj_g_in = False
        obj_p_in = False

        for object_i in objects_index:
            if (object_i == post):
                obj_i_in = True
        self.assertEqual(obj_i_in, True, 'пост не появился на главной')
        for object_g in objects_group:
            if (object_g == post):
                obj_g_in = True
        self.assertEqual(obj_g_in, True, 'пост не появился в группе')
        for object_p in objects_profile:
            if (object_p == post):
                obj_p_in = True
        self.assertEqual(obj_p_in, True, 'пост не появился в профиле')

    def test_index_page_img_passed_in_context(self):
        """В index передана картинка"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_img_0 = first_object.image

        self.assertIsNot(
            post_img_0.name, '', 'Картинка не появилась на главной')

    def test_index_page_img_passed_in_context(self):
        """В index передана картинка"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_img_0 = first_object.image

        self.assertIsNot(
            post_img_0.name, '', 'Картинка не появилась на главной')

    def test_profile_page_img_passed_in_context(self):
        """В profile передана картинка"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'StasBasov'}))
        first_object = response.context['page_obj'][0]
        post_img_0 = first_object.image

        self.assertIsNot(
            post_img_0.name, '', 'Картинка не появилась в профиле')

    def test_group_page_img_passed_in_context(self):
        """В group_posts передана картинка"""
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'test_group'}))
        first_object = response.context['page_obj'][0]
        post_img_0 = first_object.image

        self.assertIsNot(post_img_0.name, '', 'Картинка не появилась в группе')

    def test_group_page_img_passed_in_context(self):
        """В post_detail передана картинка"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1}))
        first_object = response.context['post']
        post_img_0 = first_object.image

        self.assertIsNot(
            post_img_0.name, '', 'Картинка не появилась в детальном виде')


class CacheViwesTest(TestCase):
    ''' При удалении записи из базы, она остаётся в response.content главной
    страницы до тех пор, пока кэш не будет очищен принудительно.'''
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_user = User.objects.create_user(username='author_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост для проверки кеширования страницы',
            author=cls.author_user,
            group=cls.group)

    def setUp(self):
        self.guest_client = Client()

    def test_index_page_cache(self):
        created_post = Post.objects.filter(pk=CacheViwesTest.post.pk)
        # Проверка существования поста в базе данных
        self.assertTrue(created_post.exists(),
                        'Пост отстутствует в базе данных')
        # Проверка существования поста на стартовой странице
        response = self.guest_client.get(
            reverse('posts:index'))
        self.assertIn(CacheViwesTest.post, response.context['page_obj'
                                                            ].object_list,
                      'Пост отсутствует на главной странице')
        # Контент стартовой страницы до удаления поста
        page_content = response.content
        # Удаление поста
        CacheViwesTest.post.delete()
        # Проверка существования поста в базе данных после удаления
        self.assertFalse(created_post.exists(),
                         'Пост не удален в базе данных')
        # Контент стартовой страницы после удаления поста
        page_content_after_delete = self.guest_client.get(
            reverse('posts:index')).content
        # Сравнение контента страницы до и после удаления поста
        self.assertEqual(page_content, page_content_after_delete,
                         'Кеширование не работает')
        # Очистка кеша
        cache.clear()
        # Контент стартовой страницы после очистки кеша
        page_content_after_cache_clear = self.guest_client.get(
            reverse('posts:index')).content
        # Сравнение контента страницы до и после удаления после очистки кэша
        self.assertNotEqual(page_content_after_delete,
                            page_content_after_cache_clear)
