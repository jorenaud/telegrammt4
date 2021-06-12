from django.contrib import admin

# Register your models here.
from .models import tbl_user, tbl_plan, tbl_order, \
    tbl_blocked_ip, tbl_custom_plan, tbl_promo_email, tbl_demo, \
    tbl_ip, tbl_patch, tbl_schema, tbl_alert

from django.contrib.auth.admin import UserAdmin


class TblOrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in tbl_order._meta.get_fields()]
    list_display.append("get_user_name")
    list_display.append("get_user_email")
    list_display.append("get_user_phone")
    list_display.remove("phone")
    list_display.remove("email")

    def get_user_name(self, obj):
        user = list(tbl_user.objects.filter(id=obj.userid).values())[0]
        return user['username']
    def get_user_email(self, obj):
        user = list(tbl_user.objects.filter(id=obj.userid).values())[0]
        return user['email']
    def get_user_phone(self, obj):
        user = list(tbl_user.objects.filter(id=obj.userid).values())[0]
        return user['phone']
    get_user_name.short_description = "UserName"
    get_user_email.short_description = "Email"
    get_user_phone.short_description = "Phone"


admin.site.register(tbl_user, UserAdmin)
admin.site.register(tbl_plan)
admin.site.register(tbl_order, TblOrderAdmin)
admin.site.register(tbl_blocked_ip)
admin.site.register(tbl_custom_plan)
admin.site.register(tbl_demo)
admin.site.register(tbl_ip)
admin.site.register(tbl_patch)
admin.site.register(tbl_schema)
admin.site.register(tbl_alert)
admin.site.register(tbl_promo_email)
