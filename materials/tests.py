from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from materials.models import Lesson, Subscription, Well

User = get_user_model()


class BaseSetupMixin:
    def setUp(self):
        # Создаём пользователей без create_user (из-за отсутствия username у кастомной модели)
        self.user = User.objects.create(email="u1@example.com")
        self.user.set_password("pass12345")
        self.user.save()

        self.other = User.objects.create(email="u2@example.com")
        self.other.set_password("pass12345")
        self.other.save()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.course = Well.objects.create(
            name="Курс", description="desc", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            course=self.course, title="Урок 1", description="D", owner=self.user
        )


class LessonCrudTests(APITestCase, BaseSetupMixin):
    def setUp(self):
        BaseSetupMixin.setUp(self)

    def test_create_lesson_with_non_youtube_link_fails(self):
        url = reverse("materials:lesson-list-create")
        payload = {
            "course": self.course.id,
            "title": "Bad link",
            "description": "x",
            "video_url": "https://vimeo.com/123",
        }
        resp = self.client.post(url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("video_url", resp.data)

    def test_create_lesson_ok_youtube(self):
        url = reverse("materials:lesson-list-create")
        payload = {
            "course": self.course.id,
            "title": "Good link",
            "description": "x",
            "video_url": "https://www.youtube.com/watch?v=abc",
        }
        resp = self.client.post(url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_update_and_delete_own_lesson(self):
        detail = reverse("materials:lesson-detail", args=[self.lesson.id])
        resp = self.client.patch(detail, data={"title": "UPD"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["title"], "UPD")

        resp = self.client.delete(detail)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class SubscriptionToggleTests(APITestCase, BaseSetupMixin):
    def setUp(self):
        BaseSetupMixin.setUp(self)

    def test_toggle_subscription_add_and_remove(self):
        url = reverse("materials:subscription-toggle")
        # add
        resp = self.client.post(url, data={"course_id": self.course.id}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

        # remove
        resp = self.client.post(url, data={"course_id": self.course.id}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_course_serializer_has_is_subscribed(self):
        Subscription.objects.create(user=self.user, course=self.course)
        url = reverse("materials:well-detail", args=[self.course.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("is_subscribed", resp.data)
        self.assertTrue(resp.data["is_subscribed"])


class ModeratorPermissionsTests(APITestCase):
    def setUp(self):
        # Пользователи через create() + set_password()
        self.owner = User.objects.create(email="owner@example.com")
        self.owner.set_password("pass12345")
        self.owner.save()

        self.moder = User.objects.create(email="moder@example.com")
        self.moder.set_password("pass12345")
        self.moder.save()

        self.other = User.objects.create(email="other@example.com")
        self.other.set_password("pass12345")
        self.other.save()

        # Группа модераторов
        group, _ = Group.objects.get_or_create(name="moderators")
        self.moder.groups.add(group)

        self.owner_client = APIClient()
        self.owner_client.force_authenticate(self.owner)

        self.moder_client = APIClient()
        self.moder_client.force_authenticate(self.moder)

        self.other_client = APIClient()
        self.other_client.force_authenticate(self.other)

        self.course_owner = Well.objects.create(
            name="OwnerCourse", description="d", owner=self.owner
        )
        self.lesson_owner = Lesson.objects.create(
            course=self.course_owner, title="L", description="D", owner=self.owner
        )

    def test_moder_can_read_all_and_patch_but_cannot_create_or_delete_course(self):
        # read list (видит курс не своего владения)
        list_url = reverse("materials:well-list-create")
        resp = self.moder_client.get(list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(resp.data.get("count", 0), 1)

        # create запрещен
        resp = self.moder_client.post(
            list_url, data={"name": "X", "description": "d"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # patch разрешен
        detail = reverse("materials:well-detail", args=[self.course_owner.id])
        resp = self.moder_client.patch(detail, data={"name": "UPD"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["name"], "UPD")

        # delete запрещен
        resp = self.moder_client.delete(detail)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_moder_can_only_see_own_courses(self):
        # other видит пусто, так как курс у owner
        list_url = reverse("materials:well-list-create")
        resp = self.other_client.get(list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get("count"), 0)

    def test_pagination_courses(self):
        # создаём побольше курсов для owner
        for i in range(7):
            Well.objects.create(name=f"C{i}", description="d", owner=self.owner)
        list_url = reverse("materials:well-list-create")
        resp = self.owner_client.get(list_url, {"page": 1, "page_size": 5})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data.get("results", [])), 5)

    def test_pagination_lessons(self):
        for i in range(12):
            Lesson.objects.create(
                course=self.course_owner,
                title=f"L{i}",
                description="d",
                owner=self.owner,
            )
        list_url = reverse("materials:lesson-list-create")
        resp = self.owner_client.get(list_url, {"page": 2, "page_size": 10})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Изначально 1 урок + 12 новых = 13; на 2-й странице (page_size=10) должно быть 3
        self.assertEqual(len(resp.data.get("results", [])), 3)
