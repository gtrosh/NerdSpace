import os
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Follow, Group, Post, User
from yatube.settings import BASE_DIR


@override_settings(MEDIA_ROOT=os.path.join(BASE_DIR, 'temp_views'))
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.user = User.objects.create(username='Василий')

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
            group=cls.group,
            author=cls.user,
            image=cls.uploaded,
        )
        cls.follow = Follow.objects.create(
            user=cls.user, author=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.client2 = get_user_model().objects.create_user(username='user2')
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.client2)

    def test_pages_use_correct_templates(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': reverse(
                'group', kwargs={'slug': self.group.slug}
            ),
            'new.html': reverse('new_post'),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(template=template, reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(response.context['page'][0], self.post)

    def test_group_page_shows_correct_context(self):
        """Шаблон group сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': PostsPagesTests.group.slug})
        )
        group = PostsPagesTests.group
        response_group = response.context['group']
        self.assertEqual(group, response_group)

    def test_new_post_page_shows_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_new_post_appears_on_index_page(self):
        """Новый пост отображается на главной странице сайта"""
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context['page']), 1)

    def test_each_group_contains_one_post(self):
        """В каждой группе содержится по одному посту"""
        another_group = Group.objects.create(
            title='Другое название',
            slug='other-slug',
            description='Другая тестовая группа',
        )
        another_post = Post.objects.create(
            text='Другой текст поста',
            group=another_group,
            author=PostsPagesTests.user
        )
        first_response = self.authorized_client.get(
            reverse('group', kwargs={
                'slug': self.group.slug,
            })
        )
        self.assertEqual(len(first_response.context['page']), 1)

        second_response = self.authorized_client.get(
            reverse('group', kwargs={
                'slug': another_group.slug,
            })
        )
        self.assertEqual(len(second_response.context['page']), 1)
        self.assertEqual(second_response.context['page'][0], another_post)

    def test_post_edit_page_shows_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id,
            })
        )
        self.assertEqual(response.context['post'].text, self.post.text)
        self.assertEqual(response.context['post'].group, self.post.group)

    def test_user_profile_page_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(response.context['page'][0], self.post)

    def test_post_page_shows_correct_context(self):
        """Шабон post сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('post', kwargs={
                'username': self.user.username,
                'post_id': self.post.id,
            })
        )
        post_context = {
            'post': self.post,
            'user': self.post.author,
            'count': self.user.posts.all().count(),
            'current_user': self.user,
        }
        for key, value in post_context.items():
            with self.subTest(key=key, value=value):
                context = response.context[key]
                self.assertEqual(context, value)

    def test_index_page_cache(self):
        """Проверяем работу кэша на главной странице"""
        response_one = self.authorized_client.get(reverse('index'))

        test_group = Group.objects.create(
            title='Какое-то название',
            slug='some-slug',
            description='Какая-то тестовая группа',
        )

        test_post = Post.objects.create(
            text='Новый пост',
            group=test_group,
            author=PostsPagesTests.user,
        )

        response_two = self.authorized_client.get(reverse('index'))
        self.assertEqual(response_one.content, response_two.content)
        cache.clear()

        response_two = self.authorized_client.get(reverse('index'))
        self.assertNotEqual(response_one.content, response_two.content)
        self.assertEqual(response_two.context['page'][0], test_post)

    def test_authorized_user_can_follow(self):
        """Проверяем, что авторизованный пользователь может подписываться
        на других пользователей"""
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse('profile_follow', kwargs={'username': 'user2'})
        )
        follow_count_again = Follow.objects.all().count()
        self.assertEqual(follow_count_again, follow_count + 1)

    def test_authorized_user_can_unfollow(self):
        """Проверяем, что авторизованный пользователь может отписываться от
        авторов, на которых он подписан"""
        Follow.objects.create(
            user=self.user, author=self.client2)
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse('profile_unfollow', kwargs={'username': 'user2'})
        )
        follow_count_again = Follow.objects.all().count()
        self.assertEqual(follow_count_again, follow_count - 1)

    def test_new_post_appears_only_on_followers_pages(self):
        """Проверяем, что новая запись пользователя появляется
        в ленте подписчиков и не появляется в ленте тех, кто не подписан"""
        test_post = Post.objects.create(
            text='еще один пост',
            author=self.client2,
        )
        Follow.objects.create(user=self.user, author=self.client2)
        response_one = self.authorized_client.get(reverse('follow_index'))
        response_two = self.authorized_client_2.get(reverse('follow_index'))
        self.assertEqual(
            response_one.context['page'][0], test_post)
        self.assertEqual(len(response_two.context['page']), 0)

    def test_only_authorised_user_can_comment(self):
        """Проверяем, что только авторизованный пользователь
        может комментировать посты"""
        self.url_post = reverse('post', kwargs={
            'username': self.user.username,
            'post_id': self.post.id,
        })
        self.url_comment = reverse('add_comment', kwargs={
            'username': self.user.username,
            'post_id': self.post.id,
        })
        self.authorized_client.post(self.url_comment, {'text': 'some comment'})
        response = self.authorized_client.get(self.url_post)
        self.assertContains(response, 'some comment')


class PaginatorViewsTest(TestCase):
    @ classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.client = Client()
        cls.client.force_login(cls.user)

        for i in range(13):
            Post.objects.create(
                text='Пример поста',
                author=cls.user,
            )

    def test_first_page_contains_ten_records(self):
        """Проверяем, что количество постов на первой странице равно 10"""
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_contains_three_records(self):
        """Проверяем, что количество постов на первой странице равно 3"""
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
