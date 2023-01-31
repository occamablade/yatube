from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, Comment

User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='foo',
            group=cls.group,
            author=cls.user
        )
        cls.post_id = cls.post.id

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_task(self):
        """Валидная форма создает запись в Post."""
        form_data = {
            'text': 'Test post',
            'group': self.group.pk,
        }
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        post = Post.objects.first()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_authorized_user_edit_post(self):
        post = Post.objects.create(
            text='post_text',
            author=self.user
        )
        form_data = {
            'text': 'post_text_edit',
            'group': self.group.pk
        }
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                args=[post.id]),
            data=form_data
        )
        post = Post.objects.first()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_nonauthorized_user_create_post(self):
        form_data = {
            'text': 'non_auth_edit_text',
            'group': self.group.id
        }
        posts_count = Post.objects.count()
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_comment_can_authorized_user(self):
        """Комментировать может только авторизованный пользователь."""
        form_data = {
            'text': 'Новый комментарий',
        }
        response = self.authorized_client.post(
            reverse((
                'posts:add_comment'), kwargs={'post_id': f'{self.post.id}'}),
            data=form_data
        )
        self.assertRedirects(response, reverse((
            'posts:post_detail'), kwargs={'post_id': f'{self.post.id}'}))
        self.assertTrue(
            Comment.objects.filter(text='Новый комментарий').exists()
        )

    def test_comment_show_up(self):
        """Комментарий появляется на странице поста"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Новый комментарий',
        }
        response = self.authorized_client.post(
            reverse((
                'posts:add_comment'), kwargs={'post_id': f'{self.post.id}'}),
            data=form_data
        )
        self.assertRedirects(response, reverse((
            'posts:post_detail'), kwargs={'post_id': f'{self.post.id}'}))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
