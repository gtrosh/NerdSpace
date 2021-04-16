from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User

INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
LOGIN_URL = reverse('login')

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='Fedor')

        cls.group = Group.objects.create(
            title='Название',
            slug='slug',
            description='Описание',
        )

        cls.post = Post.objects.create(
            text='Текст поста',
            group=cls.group,
            author=cls.user
        )

        cls.index_url = ('index', 'index.html', None)
        cls.group_url = ('group', 'group.html', (cls.group.slug,))
        cls.profile_url = ('profile', 'profile.html', (cls.user.username,))
        cls.post_url = ('post', 'post.html', (cls.user.username, cls.post.id,))
        cls.new_post_url = ('new_post', 'new.html', None)
        cls.edit_post_url = ('post_edit', 'new.html',
                             (cls.user.username, cls.post.id,))

        cls.names_urls = (
            cls.index_url,
            cls.group_url,
            cls.profile_url
        )

    def setUp(self):
        self.guest_client = Client()
        self.POST_EDIT_URL = reverse('post_edit', args=(self.user.username,
                                                        self.post.id))
        self.POST_VIEW_URL = reverse('post', args=(self.user.username,
                                                   self.post.id))
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.client2 = get_user_model().objects.create_user(username='user2')
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.client2)

    def test_public_pages_available_for_guest(self):
        """Публичные страницы доступны для неавторизованного пользователя"""
        urls = [
            reverse('index'),
            reverse(
                'group', kwargs={'slug': self.group.slug}),
            reverse('profile', kwargs={
                'username': self.user.username}),
            reverse('post', kwargs={
                'username': self.user.username,
                'post_id': self.post.id},)
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_pages_available_to_auth_user(self):
        """Приватные страницы доступны авторизированному пользователю."""
        urls = [
            reverse('new_post'),
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id,
            })]

        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_pages_unavailable_for_guest(self):
        """Неавторизованный пользователь перенаправлен
        на соответствующую страницу"""
        urls_clients = [
            [NEW_POST_URL, self.guest_client,
             f'{LOGIN_URL}?next={NEW_POST_URL}'],
            [self.POST_EDIT_URL, self.guest_client,
             f'{LOGIN_URL}?next={self.POST_EDIT_URL}'],
            [self.POST_EDIT_URL, self.authorized_client_2, self.POST_VIEW_URL]
        ]
        for url, client, redirect_url in urls_clients:
            with self.subTest(url=url):
                self.assertRedirects(client.get(url), redirect_url)

    def test_edit_post_by_auth_user_who_is_not_author(self):
        """Проверяем, может ли пользователь, не являющийся автором
        созданного поста, внести изменения в этот пост"""
        test_author = User.objects.create(username='Иван')
        another_post = Post.objects.create(
            text='Текст',
            author=test_author,
            group=self.group,
        )
        test_url = f'/{test_author.username}/{another_post.id}/edit/'
        response = self.authorized_client.get(test_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_use_correct_template(self):
        """URL-адрес использует корректный шаблон."""
        new_names_urls = (
            PostsURLTests.post_url,
            PostsURLTests.edit_post_url,
            PostsURLTests.new_post_url
        )
        for name, template, args in (PostsURLTests.names_urls
                                     + new_names_urls):
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse(name, args=args))
                self.assertTemplateUsed(response, template)

    def test_server_return_404_if_page_not_found(self):
        url = reverse('post', kwargs={
            'username': self.user.username,
            'post_id': 9999},)
        response = self.guest_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
