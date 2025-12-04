from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from materials.models import Well, Lesson

class User(AbstractUser):

    username = None

    email = models.EmailField(
        unique=True, verbose_name="Почта", help_text="Укажите почту"
    )
    phone = models.CharField(
        max_length=35,
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="Укажите телефон",
    )
    city = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Город",
        help_text="Введите название города проживания",
    )
    avatar = models.ImageField(
        upload_to="users/avatars",
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Загрузите аватар",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"



class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Наличные"
        BANK_TRANSFER = "bank", "Перевод на счёт"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
        help_text="Пользователь совершивший оплату",
    )
    paid_at = models.DateTimeField(
        verbose_name="Дата оплаты",
        help_text="Двтв и время совершения оплаты",
        auto_now_add=False,
    )
    course = models.ForeignKey(
        Well,
        on_delete=models.SET_NULL,
        related_name="payments",
        blank=True,
        null=True,
        verbose_name="Оплаченный курс",
        help_text="Ссылка на курс,усли оплачивался курс",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        related_name="payments",
        blank=True,
        null=True,
        verbose_name="Оплаченный урок",
        help_text="Ссылка на урок,если оплачивался отдельный урок",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма оплаты",
        help_text="Сумма платежа",
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
        verbose_name="Способ оплаты",
        help_text="Налмчные или перевод на счёт"
    )
    # --- Stripe служебные поля ---
    stripe_product_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_session_id = models.CharField(max_length=100, blank=True, null=True)
    checkout_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=32, blank=True, null=True, help_text="Статус платежной сессии (optional)")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self) -> str:
        target = self.course or self.lesson
        return f"{self.user} -> {target} -> [{self.amount}] {self.paid_at}"

