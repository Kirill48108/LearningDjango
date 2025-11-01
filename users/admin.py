from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "paid_at",
        "course",
        "lesson",
        "amount",
        "payment_method",
    )
    list_filter = ("paid_at", "payment_method", "course", "lesson")
    search_fields = ("user__email",)
