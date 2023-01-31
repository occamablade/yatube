from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUserNoName')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post_author = User.objects.create_user(username='Post_author')
        cls.post_author_client = Client()
        cls.post_author_client.force_login(cls.post_author)
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.url_template = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        cls.public_urls = (
            '/',
            f'/group/{cls.group.slug}/',
            f'/posts/{cls.post.id}/',
            f'/profile/{cls.user.username}/'
        )

    def test_unexisting_page(self):
        """Проверка: запрос к несуществующей странице
        возвращает ошибку 404
        """
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_exists_at_desired_location_anonymous(self):
        """Проверка: страницы доступны всем"""
        for url in self.public_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_exists_at_desired_location_authorized(self):
        """Проверка: страница создания поста доступна
        авторизованному пользователю
        """
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_exists_at_desired_location_author(self):
        """Проверка: страница изменения поста доступна
        автору поста
        """
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_exists_at_desired_non_author(self):
        """Проверка: страница изменения поста не автором
        редиректит пользователя на страницу входа
        """
        response = self.guest_client.get(f'/posts/{self.post.id}/edit/')
        self.assertRedirects(
            response, f'/posts/{self.post.pk}/'
        )

    def test_create_post_redirect_anonymous_on_login(self):
        """Проверка: cтраница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/create/')
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_edit_post_redirect_on_post_profile_none_author(self):
        """Проверка: страница по адресу /edit/ перенаправит пользователя,
        не являющегося автором данного поста, на страницу просмотра поста
        """
        response = self.post_author_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertRedirects(
            response, f'/posts/{self.post.id}/'
        )

    def test_urls_uses_correct_template(self):
        """Проверка: URL-адрес использует соответствующий шаблон."""
        for url, template in self.url_template.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
