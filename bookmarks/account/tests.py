from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile


class EditProfileTests(TestCase):
    def setUp(self):
        # Создаем двух пользователей для тестов
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            date_of_birth='1990-01-01',
            photo=None
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@example.com',
            password='password123'
        )

    def test_successful_profile_edit(self):
        # Аутентифицируемся как testuser
        self.client.login(username='testuser', password='password123')

        # Данные для успешного редактирования
        data = {
            'first_name': 'NewName',
            'last_name': 'NewLastName',
            'email': 'newemail@example.com',
            'date_of_birth': '1995-05-05',
        }

        # Отправляем POST запрос на редактирование
        response = self.client.post(reverse('edit'), data)
        # Проверяем, что редиректа нет и форма успешно обработана
        self.assertEqual(response.status_code, 200)

        # Обновляем данные пользователя из базы
        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        # Проверяем изменения
        self.assertEqual(self.user.first_name, 'NewName')
        self.assertEqual(self.user.last_name, 'NewLastName')
        self.assertEqual(self.user.email, 'newemail@example.com')
        self.assertEqual(self.profile.date_of_birth.strftime('%Y-%m-%d'), '1995-05-05')

    def test_edit_profile_with_duplicate_email(self):
        # Аутентифицируемся как testuser
        self.client.login(username='testuser', password='password123')

        # Данные с уже существующим email
        data = {
            'first_name': 'NewName',
            'last_name': 'NewLastName',
            'email': 'otheruser@example.com',  # Email другого пользователя
            'date_of_birth': '1995-05-05',
        }

        # Отправляем POST запрос на редактирование
        response = self.client.post(reverse('edit'), data)
        # Проверяем, что остались на той же странице (ошибка)
        self.assertEqual(response.status_code, 200)

        # Проверяем, что сообщение об ошибке отображается
        self.assertContains(response, 'Email already in use.')

        # Проверяем, что данные пользователя не изменились
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'testuser@example.com')


class AccountPageTests(TestCase):
    def setUp(self):
        # Создаём тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.url = reverse('dashboard')

    def test_redirect_for_anonymous_user(self):
        # Попытка доступа без авторизации
        response = self.client.get(self.url)
        # Проверяем, что был редирект на страницу логина
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'], f'/account/login/?next={self.url}'
        )

    def test_access_for_authenticated_user(self):
        # Логинимся как тестовый пользователь
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        # Проверяем, что доступ к странице разрешён
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/dashboard.html')
