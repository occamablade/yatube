from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, Follow
from posts.forms import PostForm

from yatube.settings import POST_ON_PAGE

User = get_user_model()


class PostsViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username="TestUser"
        )
        cls.random_user = User.objects.create_user(
            username="RandomUser"
        )
        cls.group = Group.objects.create(
            description="Тестовое описание",
            slug="Test-slug",
            title="Тестовое название"
        )
        cls.group_2 = Group.objects.create(
            description="Тестовое описание второй группы",
            slug="test-slug-group-2",
            title="Тестовое название второй группы"
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="test test",
            group=cls.group
        )

    def setUp(self):
        """Не забываем перед каждым тестом чистить кэш"""
        cache.clear()
        self.client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        author_querry = Follow.objects.filter(user=self.user)
        author_values_list = author_querry.values_list('author')
        self.post_list = Post.objects.filter(author_id__in=author_values_list)

    def check_context_contains_page_or_post(self, context, post=False):
        """Эта функция является частью простого контекстного тестирования.
        Она создана для того, что бы не создавать повторяющиеся конструкции"""
        if post:
            self.assertIn('post', context)
            post = context['post']
        else:
            self.assertIn('page_obj', context)
            post = context['page_obj'][0]
        self.assertEqual(post.author, PostsViewsTest.user)
        self.assertEqual(post.text, PostsViewsTest.post.text)
        self.assertEqual(post.group, PostsViewsTest.post.group)
        self.assertEqual(post.image, PostsViewsTest.post.image)

    def test_view_funcs_correct_templates(self):
        """Проверка на использование корректного шаблона"""

        names_templates = {
            reverse(
                "posts:index"
            ): "posts/index.html",
            reverse(
                "posts:post_create"
            ): "posts/create_post.html",
            reverse(
                "posts:group_list",
                kwargs={"slug": self.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:post_detail",
                kwargs={"post_id": self.post.id}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit",
                kwargs={"post_id": self.post.id}
            ): "posts/create_post.html",
            reverse(
                "posts:profile",
                kwargs={"username": self.user.username}
            ): "posts/profile.html",
        }
        for url, template in names_templates.items():
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        response = self.auth_client.get(reverse("posts:index"))
        self.check_context_contains_page_or_post(response.context)

    def test_group_posts_correct_context(self):
        response = self.auth_client.get(
            reverse(
                "posts:group_list",
                kwargs={"slug": self.group.slug}
            )
        )
        self.check_context_contains_page_or_post(response.context)
        self.assertIn('group', response.context)
        group = response.context['group']
        self.assertEqual(group, PostsViewsTest.group)

    def test_post_detail_correct_context(self):
        response = self.auth_client.get(
            reverse(
                "posts:post_detail",
                kwargs={"post_id": self.post.id}
            )
        )
        self.check_context_contains_page_or_post(response.context, post=True)

    def test_post_edit_and_create_show_correct_context(self):
        """Шаблон edit и create сформирован с правильным контекстом."""
        create_or_edit_urls = (
            (reverse('posts:post_create'), False),
            (reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}),
                True)
        )
        for url, is_edit_value in create_or_edit_urls:
            with self.subTest(name=url):
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], PostForm)
                self.assertIn('is_edit', response.context)
                is_edit = response.context['is_edit']
                self.assertIsInstance(is_edit, bool)
                self.assertEqual(is_edit, is_edit_value)

    def test_profile_use_correct_context(self):
        response = self.auth_client.get(
            reverse(
                "posts:profile",
                kwargs={"username": self.user.username}
            )
        )
        self.check_context_contains_page_or_post(response.context)

    def test_post_another_group(self):
        """Пост не попал в другую группу"""
        response = self.auth_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group_2.slug}
        ))
        self.assertNotIn(self.post, response.context["page_obj"])

    def test_cache(self):
        """ Проверка работы кеша на главной странице. """
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост_Кэш',
            group=self.group,
            image=None
        )
        response1 = (self.auth_client.get(reverse('posts:index')))
        post.delete()
        cache.clear()
        response2 = (self.auth_client.get(reverse('posts:index')))
        self.assertNotEqual(response1.content, response2.content)

    def test_add_comment_correct_context(self):
        """Проверка add_comment
        комментарий появляется на странице поста
        комментировать посты может только авторизованный пользователь
        """
        url = reverse('posts:add_comment', args=[self.post.pk])
        response = self.auth_client.get(url,)
        if self.post.author == self.auth_client:
            self.assertEqual(response.status_code, HTTPStatus.OK)
        elif self.user == self.auth_client:
            self.assertRedirects(response, url)
        else:
            response = self.client.get(url)
            self.assertRedirects(
                response, reverse(
                    'users:login'
                ) + "?next=" + reverse(
                    'posts:add_comment', args=[self.post.pk])
            )

    def test_follow(self):
        """Проверка авторизованный пользователь может
        подписываться на других пользователей """
        self.auth_client.get(f'/profile/{self.user}/follow/')
        response = self.auth_client.get('/follow/')
        for post in self.post_list:
            self.assertEqual(response.context.get('post'), post)

    def test_unfollow(self):
        """Проверка авторизованный пользователь может
        удалять других пользователей из подписок """
        self.auth_client.get(f'/profile/{self.user}/unfollow/')
        response = self.auth_client.get('/follow/')
        for post in self.post_list:
            self.assertEqual(response.context.get('post'), post)

    def test_check_correct_followed(self):
        """Проверка Ленты постов авторов
        Новая запись пользователя появляется в ленте
        тех, кто на него подписан"""
        response = self.auth_client.get('/follow/')
        for post in self.post_list:
            self.assertEqual(response.context.get('post'), post)

    def test_check_correct_unfollowed(self):
        """Проверка Ленты постов авторов
        В ленте подписок нет лишних постов"""
        response = self.auth_client.get('/follow/')
        self.assertEqual(response.context.get('post'), None)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username="qwerty"
        )
        cls.group = Group.objects.create(
            description="Тестовое описание",
            slug="test-slug",
            title="Тестовое название"
        )
        Post.objects.bulk_create(
            Post(
                text=f'Пост {number}',
                author=cls.user,
                group=cls.group,
            )
            for number in range(POST_ON_PAGE + 3)
        )

        cls.client = Client()

    def test_paginator(self):
        url_names = {
            reverse('posts:index'): POST_ON_PAGE,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): POST_ON_PAGE,
            reverse(
                'posts:profile',
                args=[self.user]
            ): POST_ON_PAGE,
        }
        pages = (
            (1, 10),
            (2, 3)
        )
        for url in url_names:
            for page, expected_count in pages:
                response = self.client.get(url, {"page": page})
                self.assertEqual(
                    len(response.context['page_obj']),
                    expected_count
                )
