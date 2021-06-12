from django.urls import path

from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),

    path('reg_email_verify', views.reg_email_verify, name='register'),
    path('register', views.register, name='register'),
    path('reset_password', views.reset_password, name='reset_password'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),

    path('subscription', views.subscription, name='subscription'),
    path('profile', views.profile, name='profile'),
    path('order', views.order, name='order'),

    path('load_paypal_regular_plans', views.load_paypal_regular_plans, name='paypal_recurr'),

    path('create_paypal_plan', views.create_paypal_plan, name='create_paypal_plan'),
    path('create_paypal_plan_custom', views.create_paypal_plan_custom, name='create_paypal_plan_custom'),
    path('verify_paypal_subscription', views.verify_paypal_subscription, name='verify_paypal_subscription'),
    path('verify_paypal_subscription_custom', views.verify_paypal_subscription_custom, name='verify_paypal_subscription_custom'),
    path('verify_paypal_onepay', views.verify_paypal_onepay, name='verify_paypal_onepay'),
    path('verify_paypal_onepay_custom', views.verify_paypal_onepay_custom, name='verify_paypal_onepay_custom'),


    path('update_account', views.update_account, name='update_account'),
    path('update_profile', views.update_profile, name='update_profile'),
    path('update_password', views.update_password, name='update_password'),
    path('check_current_plan', views.check_current_plan, name='check_current_plan'),
    path('get_custom_plan_price', views.get_custom_plan_price, name='get_custom_plan_price'),
    path('load_paypal_custom_plans', views.load_paypal_custom_plans, name='load_paypal_custom_plans'),
    path('cancel_subscription', views.cancel_subscription, name='cancel_subscription'),

    path('robots.txt', views.robots, name='robots'),
    path('sitemap.xml', views.sitemap, name='sitemap'),

    path('verify_stripe_onepay', views.verify_stripe_onepay, name='verify_stripe_onepay'),
    path('verifiy_stripe_subscription', views.verifiy_stripe_subscription, name='verifiy_stripe_subscription'),
    path('verify_stripe_onepay_custom', views.verify_stripe_onepay_custom, name='verify_stripe_onepay_custom'),
    path('verifiy_stripe_subscription_custom', views.verifiy_stripe_subscription_custom, name='verifiy_stripe_subscription_custom'),
    path('affiliate', views.affiliate, name='affiliate'),
    path('signal', views.signal, name='signal'),
    path('link', views.link, name='link'),
    path('create_crypto_order', views.create_crypto_order, name='create_crypto_order'),
    path('verify_crypto_order', views.verify_crypto_order, name='verify_crypto_order'),
]