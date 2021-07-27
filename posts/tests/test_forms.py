import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.user = User.objects.create_user(username='Федор')

        cls.group = Group.objects.create(
            title='Название',
            slug='slug',
            description='Тестовая группа',
        )
        cls.my_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='my.gif',
            content=cls.my_gif,
            content_type='image/gif',
        )
        cls.post = Post.objects.create(
            text='Текст поста',
            group=PostCreateFormTests.group,
            author=PostCreateFormTests.user,
            image=PostCreateFormTests.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_new_post_created_from_form_data(self):
        """Проверяем, что при отправке формы в базе данных
        создается новая запись"""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='my.gif',
            content=self.my_gif,
            content_type='image/gif',
        )
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id,
            'image': uploaded,

        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.get(
                text='Текст из формы',
                group=self.group.id,
            )
        )

    def test_edit_existing_post(self):
        """Проверяем, что после редактирования поста
        изменяется соответствующая запись в базе данных"""
        form_data = {
            'group': self.group.id,
            'text': 'Текст',
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={
                    'username': self.user.username,
                    'post_id': self.group.id
                    }),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Post.objects.filter(
            group=self.group.id,
            text='Текст',
            author=self.user).exists()
        )
