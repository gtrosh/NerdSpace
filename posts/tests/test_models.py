from django.test import TestCase
from posts.models import Group, Post, User


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Название',
            slug='Слаг',
            description='Описание',
        )

    @classmethod
    def tearDownClass(cls):
        super().setUpClass()
        cls.group.delete()

    def test_title_label(self):
        """verbose_name поля title совпадает с ожидаемым."""
        verbose = GroupModelTest.group._meta.get_field('title').verbose_name
        self.assertEquals(verbose, 'Название группы')

    def test_help_text(self):
        """help_text поля title совпадает с ожидаемым."""
        help_text = GroupModelTest.group._meta.get_field('title').help_text
        self.assertEquals(help_text, 'Дайте название группе')

    def test_group_title(self):
        """__str__ - это строчка с названием группы."""
        group = GroupModelTest.group
        title = str(group)
        self.assertEquals(title, group.title)


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.post = Post.objects.create(
            text='Текст поста',
            author=User.objects.create(username='Федор')
        )

    @classmethod
    def tearDownClass(cls):
        super().setUpClass()
        cls.post.delete()

    def test_title_label(self):
        """verbose_name поля text совпадает с ожидаемым."""
        verbose = PostModelTest.post._meta.get_field('text').verbose_name
        self.assertEquals(verbose, 'Текст поста')

    def test_title_help_text(self):
        """help_text поля text совпадает с ожидаемым."""
        help_text = PostModelTest.post._meta.get_field('text').help_text
        self.assertEquals(help_text, 'Напишите текст поста')

    def test_str(self):
        """__str__ - это первые пятнадцать символов поста"""
        post = PostModelTest.post
        text = post.text
        self.assertEquals(str(post), text[:15])
