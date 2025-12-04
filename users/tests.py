from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from materials.models import Well, Lesson
from users.models import Payment

User = get_user_model()


class UsersAuthProfilesTests(APITestCase):
    def setUp(self):
        # Создаём пользователей через create() + set_password()
        self.user = User.objects.create(email="u1@example.com", first_name="U1")
        self.user.set_password("pass12345")
        self.user.save()

        self.other = User.objects.create(email="u2@example.com", first_name="U2")
        self.other.set_password("pass12345")
        self.other.save()

        self.client_u1 = APIClient()
        self.client_u1.force_authenticate(self.user)

        self.client_u2 = APIClient()
        self.client_u2.force_authenticate(self.other)

    def test_registration(self):
        url = reverse("register")
        data = {"email": "new@example.com", "password": "StrongPass1!", "first_name": "New"}
        resp = self.client.post(url, data=data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    def test_jwt_obtain_and_refresh(self):
        obtain = reverse("token_obtain_pair")
        refresh = reverse("token_refresh")
        resp = self.client.post(obtain, data={"email": "u1@example.com", "password": "pass12345"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)
        r = self.client.post(refresh, data={"refresh": resp.data["refresh"]}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("access", r.data)

    def test_profiles_list_requires_auth(self):
        url = reverse("profiles-list")
        # аноним
        anon = APIClient()
        resp = anon.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        # авторизованный
        resp = self.client_u1.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_profile_visibility_and_editing_rules(self):
        # чужой профиль — только публичные поля
        detail_other = reverse("profiles-detail", args=[self.other.id])
        resp = self.client_u1.get(detail_other)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("email", resp.data)
        # редактировать чужой — нельзя
        resp = self.client_u1.patch(detail_other, data={"first_name": "HACK"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # свой профиль — можно редактировать
        detail_self = reverse("profiles-detail", args=[self.user.id])
        resp = self.client_u1.patch(detail_self, data={"first_name": "U1-NEW"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get("first_name"), "U1-NEW")

    def test_profiles_create_via_viewset_forbidden(self):
        # создание пользователя через ViewSet запрещено (405)
        url = reverse("profiles-list")
        resp = self.client_u1.post(url, data={"email": "x@x.x", "password": "123"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

class PaymentsListFilterOrderingTests(APITestCase):
    def setUp(self):
        # Создаём пользователей через create() + set_password()
        self.user = User.objects.create(email="u1@example.com")
        self.user.set_password("pass12345")
        self.user.save()

        self.other = User.objects.create(email="u2@example.com")
        self.other.set_password("pass12345")
        self.other.save()

        self.client_u1 = APIClient()
        self.client_u1.force_authenticate(self.user)

        self.course = Well.objects.create(name="Course A", description="d", owner=self.user)
        self.lesson = Lesson.objects.create(course=self.course, title="Lesson A", description="d", owner=self.user)

        Payment.objects.create(
            user=self.user, course=self.course, amount="100.00", payment_method="cash",
            paid_at="2025-01-01T10:00:00Z"
        )
        Payment.objects.create(
            user=self.user, lesson=self.lesson, amount="50.00", payment_method="bank",
            paid_at="2025-01-02T10:00:00Z"
        )

    def test_list_and_filter(self):
        url = reverse("payments-list")
        resp = self.client_u1.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(resp.data.get("count", 0), 2)

        # фильтр по курсу
        resp = self.client_u1.get(url, {"course": self.course.id})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for item in resp.data.get("results", []):
            self.assertEqual(item["course"], self.course.id)

        # фильтр по способу оплаты
        resp = self.client_u1.get(url, {"payment_method": "cash"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for item in resp.data.get("results", []):
            self.assertEqual(item["payment_method"], "cash")

    def test_ordering(self):
        url = reverse("payments-list")
        # По возрастанию
        resp = self.client_u1.get(url, {"ordering": "paid_at"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        items = resp.data.get("results", [])
        self.assertLessEqual(items[0]["paid_at"], items[-1]["paid_at"])
        # По убыванию
        resp = self.client_u1.get(url, {"ordering": "-paid_at"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        items_desc = resp.data.get("results", [])
        self.assertGreaterEqual(items_desc[0]["paid_at"], items_desc[-1]["paid_at"])
