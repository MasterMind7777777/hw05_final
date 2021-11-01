from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Post
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO

User = get_user_model()


class PostFormTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
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

        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            image=self.uploaded
        )

    def test_can_create_post(self):
        posts_count = Post.objects.count()
        img = BytesIO(self.small_gif)
        img.name = 'myimage.jpg'
        form_data = {
            'text': 'Текст из формы',
            'image': img
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(id=2)
        post_img_0 = post.image

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertIsNot(post_img_0.name, '', 'Картинка не появилась в БД')
        self.assertEqual(response.status_code, 200)

    def test_can_edit_post(self):
        old_text = self.post.text
        form_data = {
            'text': 'Текст изменён',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        self.assertNotEqual(old_text, form_data['text'],
                            'Пользователь не может изменить пост')
        self.assertEqual(response.status_code, 200)

    def test_comment_only_authecated(self):
        """Коментарии могут оставлять только зарегестрированые пользователи"""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Текст комментария',
        }
        response_authorized = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        response_guest = self.guest_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )

        self.assertEqual(
            response_authorized.status_code, 200)
        self.assertEqual(
            response_guest.status_code, 200)
        self.assertEqual(
            Comment.objects.count(), comment_count + 1,
            'Коментарий не сохранился или не авторизованый'
            'пользователь оставил коментарий')
