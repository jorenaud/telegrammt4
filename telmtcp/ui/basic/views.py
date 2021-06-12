from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from hexbytes import HexBytes

from telmtcp.module.telmtcp import common as mcm
from telmtcp.module.telmtcp import constant as mcs
from telmtcp.module.telmtcp import email as mce
from telmtcp.module.glb.ret_code import *
from telmtcp.database.orm.models import *
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from telmtcp.module.telmtcp import paypal_client
from telmtcp.module.telmtcp import paypal_order
from telmtcp.module.telmtcp import paypal_obj
from telmtcp.module.crypto import ethereum as my_ethereum
from datetime import datetime, timedelta, date
from dateutil import relativedelta

from django.views.decorators.clickjacking import xframe_options_exempt

import random
import time
import json
import os
from django.conf import settings
from django.db.models import Q
import stripe
from django.db import connections

stripe.api_key = mcm.get_stripe_key()['stripe_client_secret_key']

# Create your views here.


def update_crypto_order(item, balance, orig_balance):
    if item['create_date'] + timedelta(seconds=mcs.CRYPTO_TIMEOUT_ORDER) <= datetime.now():
        tbl_crypto_order.objects.filter(pk=item['id']).update(status=-1)  # timeout
        return
    if item['crypto'] == 'ETH':
        result = my_ethereum.check_transaction(item, balance, orig_balance)
        if result['status'] == item['status']:
            return
        tbl_crypto_order.objects.filter(pk=item['id']).update(status=result['status'], received=result['received'],
                                                              txs=result['txs'], refunded=result['refunded'],
                                                              ref_code=result['ref_code'],
                                                              ref_message=result['ref_message'],
                                                              ref_tx=result['ref_tx'])
        if result['status'] == 2:
            new_params = {'userid': item['user_id'], 'plan_id': item['plan_id'],
                          'create_date': item['create_date'], 'expire_date': item['expire_date'],
                          'price': item['price'], 'affiliate': item['affiliate'],
                          'custom_account_cn': item['custom_account_cn'], 'custom_plan_type': item['custom_plan_type']}
            order_obj = tbl_order(**new_params)
            order_obj.save()
        return
    else:
        return


def crypto_payment_check_by_transferred():
    while mcs.CRYPTO_PAYMENT_CHECK_THREAD:
        try:
            orders = list(tbl_crypto_order.objects.filter(Q(transferred=0) & (Q(status=0) | Q(status=1) | Q(status=2))).values())
            for item in orders:
                if item['status'] < 0:
                    continue
                orig_balance = (list(tbl_user.objects.filter(pk=item['user_id']).values())[0])['eth_balance']
                balance = my_ethereum.get_eth_balance(item['address'])
                if item['status'] == 0:
                    update_crypto_order(item, balance, orig_balance)
                if balance > mcs.LIMIT_ETH_WITHDRAW:
                    gas_price = my_ethereum.get_gas_price()
                    amount = my_ethereum.calc_exact_eth_dst_amount(item['address'], gas_price, mcs.ETH_GAS_LIMIT)
                    if amount > 0:
                        ret = my_ethereum.transfer_eth(item['address'], HexBytes(item['private']),
                                                       mcs.ETH_ADMIN_ADDRESS, amount, mcs.ETH_GAS_LIMIT, gas_price,
                                                       False)
                        print(ret['message'])
                        if ret['code'] == 0:
                            balance -= amount
                elif item['status'] != 0:
                    tbl_crypto_order.objects.filter(pk=item['id']).update(transferred=1)
                if balance != orig_balance:
                    tbl_user.objects.filter(pk=item['user_id']).update(eth_balance=balance)
        except Exception as e:
            print(str(e))
        time.sleep(mcs.ETH_TIME_SLEEP_SECONDS)
    mcs.CRYPTO_PAYMENT_CHECK_THREAD = False


def crypto_payment_check():
    while mcs.CRYPTO_PAYMENT_CHECK_THREAD:
        try:
            users = list(tbl_user.objects.all().values())
            for user in users:
                if user['eth_address'] == '' or user['eth_private'] == '':
                    continue
                time.sleep(0.1)
                orig_balance = (list(tbl_user.objects.filter(pk=user['id']).values())[0])['eth_balance']
                balance = my_ethereum.get_eth_balance(user['eth_address'])
                orders = list(tbl_crypto_order.objects.filter(Q(status=0) & Q(user_id=user['id'])).values())
                count = len(orders)
                if count > 0:
                    item = orders[count - 1]
                    update_crypto_order(item, balance, orig_balance)
                if balance > mcs.LIMIT_ETH_WITHDRAW:
                    gas_price = my_ethereum.get_gas_price()
                    amount = balance - gas_price * mcs.ETH_GAS_LIMIT / pow(10, 9)
                    if amount > 0:
                        ret = my_ethereum.transfer_eth(user['eth_address'], HexBytes(user['eth_private']), mcs.ETH_ADMIN_ADDRESS, amount, mcs.ETH_GAS_LIMIT, gas_price, False)
                        print(ret['message'])
                        if ret['code'] == 0:
                            balance -= amount
                if balance != orig_balance:
                    tbl_user.objects.filter(pk=user['id']).update(eth_balance=balance)
        except Exception as e:
            print(str(e))
        time.sleep(mcs.ETH_TIME_SLEEP_SECONDS)
    mcs.CRYPTO_PAYMENT_CHECK_THREAD = False


def close_old_connections():
    for conn in connections.all():
        conn.close_if_unusable_or_obsolete()


def send_promo_emails():
    while mcs.EMAIL_PROMO_CHECK_THREAD:
        try:
            mails = list(tbl_promo_email.objects.filter(sent=0).values())
            for mail in mails:
                messages = mail['message'].split(';')
                context = {}
                context['site_name'] = mcs.site_name
                context["team_name"] = mcs.team_name
                context["company_name"] = mcs.company_name
                context['username'] = 'Trader'
                context["site_url"] = mcs.site_url
                context['message'] = messages
                html = mce.render_email(context, "email/email_promo.html")
                part1 = MIMEText(html, 'html')

                users = list(tbl_user.objects.all().values())
                # to_emails = []
                for user in users:
                    try:
                        if user['email'].find('@') <= 0:
                            continue
                        # to_emails.append(user['email'])
                        mcm.send_mail([user['email']],
                                      subject='[Telegram MT4 Copier] ' + mail['subject'], message=part1, noreply=False)
                        mcm.print_log("send_promo_emails sent email:" + user['email'] + " user_id:" + str(user['id']),
                                      "DEBUG", 3)
                    except Exception as e:
                        mcm.print_log("send_promo_emails exception email: " + user['email'] + " exception: " + str(e), "EXCEPTION", 3)
                    time.sleep(120)
                mcm.print_log("send_promo_emails completed email_id:" + str(mail['id']),
                              "DEBUG", 3)
                close_old_connections()
                tbl_promo_email.objects.filter(pk=mail['id']).update(sent=1)
        except Exception as e:
            mcm.print_log("send_promo_emails exception: " + str(e), "EXCEPTION", 3)
        time.sleep(mcs.EMAIL_PROMO_SLEEP_SECONDS)
    mcs.EMAIL_PROMO_CHECK_THREAD = False


def welcome(request):
    data = {}
    import threading
    if mcs.CRYPTO_PAYMENT_CHECK_THREAD is False:
        mcs.CRYPTO_PAYMENT_CHECK_THREAD = True
        t = threading.Thread(target=crypto_payment_check_by_transferred, args=(), kwargs={})
        t.setDaemon(True)
        t.start()
    if mcs.EMAIL_PROMO_CHECK_THREAD is False:
        mcs.EMAIL_PROMO_CHECK_THREAD = True
        t = threading.Thread(target=send_promo_emails, args=(), kwargs={})
        t.setDaemon(True)
        t.start()

    data['site_title'] = mcs.site_title
    plans = mcm.get_plans(request)
    data['plans'] = plans
    return render(request, 'welcome/welcome.html', data)


def send_email_to_user(to_emails, subject, message, username='Admin'):
    try:
        context = {}
        context['site_name'] = mcs.site_name
        context["team_name"] = mcs.team_name
        context["company_name"] = mcs.company_name
        context['username'] = username
        context["site_url"] = mcs.site_url
        context['message'] = message.split(';')
        html = mce.render_email(context, "email/email_promo.html")
        part1 = MIMEText(html, 'html')
        res = mcm.send_mail_thread(to_emails, subject='[Telegram MT4 Copier] ' + subject,
                                   message=part1)
        return res
    except:
        return -1


def send_verify_code(request):
    try:
        if mcs.IS_EMAIL_VERIFY is False and mcs.IS_PHONE_VERIFY is False:
            return 1
        params = request.POST
        reg_email = params['reg_email']
        reg_phone = params['reg_phone']
        email_code = str(random.randint(100000, 999999))
        if mcs.IS_EMAIL_VERIFY:
            # msg = MIMEMultipart('alternative')
            # msg['from'] = mcm.get_mail_account(request)["email"]
            # msg['to'] = reg_email
            # msg['Subject'] = mcs.site_title

            context = {}
            context['confirm_code'] = email_code
            context['site_name'] = mcs.site_name
            context["team_name"] = mcs.team_name
            context["company_name"] = mcs.company_name
            context['username'] = params['reg_username']
            context["site_url"] = mcs.site_url
            context["site_logo_url"] = mcs.site_url + "/static/telmtcp/img/icon/logo-without-bg.png"
            context["verify_logo_url"] = mcs.site_url + "/static/telmtcp/img/icon/verify.png"

            html = mce.render_email(context, "email/email_verify.html")
            part1 = MIMEText(html, 'html')
            # msg.attach(part1)

            mcm.send_mail_thread([reg_email], subject='[Telegram MT4 Copier] Please verify your email address.', message=part1)
        if mcs.IS_PHONE_VERIFY:
            message = SmsTextSimpleBody()
            reg_phone = '+' + reg_phone
            message.set_to([reg_phone]).set_text(str(email_code))
            infobip_client = SmsClient(url=mcs.infobip_url, api_key=mcs.infobip_key)
            res = infobip_client.send_sms_text_simple(message)
            if res.status_code != 200 or res.ok is not True:
                return -2
        request.session[mcm.encrypt('emailcode')] = mcm.encrypt(email_code)
        return 0
    except:
        mcm.print_exception()
        return -3


def reg_email_verify(request):
    try:
        if request.session.has_key("emailcode") is False:
            return HttpResponse("not_found_code")
        verify_code = request.session["emailcode"]
        params = request.POST
        if verify_code != params['reg_email_verify']:
            return HttpResponse("wrong_code")
        username = params["username"]
        password = params["password"]
        email = params['email']
        tbl_user.objects.filter(username=username).update(is_active=1)
        ret_code, user_obj = mcm.authenticate_user(username, password)

        if ret_code != AUTH_SUCCESS:
            return HttpResponse("login_failed")

        django_login(request, user_obj)

        request.session[mcm.encrypt('username')] = mcm.encrypt(username)
        request.session.save()
        try:
            send_email_to_user([email], "Welcome To Join US!", "Thank you for Registering at our Telegram MT4 Copier.; ;Email: "
                               + email + ";Username: " + username + ";Password: " + password, username)
            send_email_to_user([mcs.ADMIN_EMAIL_ADDRESS], "New user coming to your website.",
                            "New user (" + params['username'] + ") signed up to your website.")
        except Exception as e:
            print("login send_admin_exception:" + str(e))
        return HttpResponse("success")
    except:
        mcm.print_exception()
        return HttpResponse("exception")


def register(request):
    try:
        params = request.POST
        new_params = {}
        new_params['username'] = params['reg_username']
        new_params['email'] = params['reg_email']
        new_params['phone'] = params['reg_phone']
        if "undefined" in new_params['phone']:
            new_params['phone'] = new_params['phone'][9:]
        new_params['s_password'] = params['reg_pwd']
        if tbl_user.objects.filter(username=new_params['username']).count() > 0:
            return HttpResponse("username_exist")
        if tbl_user.objects.filter(email=new_params['email']).count() > 0:
            return HttpResponse("email_exist")
        if tbl_user.objects.filter(phone=new_params['phone']).count() > 0:
            return HttpResponse('phoneexist')
        if request.session.has_key('affiliate'):
            user = request.session['affiliate']
            user_id = mcm.get_user_id(user)
            new_params['affiliate'] = user_id
        #  new_eth_account = my_ethereum.create_wallet()
        #  new_params['eth_address'] = new_eth_account.address
        #  new_params['eth_private'] = new_eth_account.privateKey.hex()
        res = send_verify_code(request)
        if res == -1:
            return HttpResponse('email_failed')
        if res == -2:
            return HttpResponse('phone_failed')
        if res == -3:
            return HttpResponse('verify_exception')
        if res == 0:
            new_params['is_active'] = 0
        else:
            new_params['is_active'] = 1
        user_obj = tbl_user(**new_params)
        user_obj.set_password(params['reg_pwd'])
        user_obj.save()
        if res == 0:
            return HttpResponse("send_code")
        username = params['reg_username']
        password = params['reg_pwd']
        ret_code, user_obj = mcm.authenticate_user(username, password)

        if ret_code != AUTH_SUCCESS:
            return HttpResponse("failure")

        django_login(request, user_obj)

        request.session[mcm.encrypt('username')] = mcm.encrypt(username)
        request.session.save()
        return HttpResponse("success")
    except:
        mcm.print_exception()
        return HttpResponse("failure")


def get_username(email=""):
    if email.find("@") <= 0:
        return email
    users = list(tbl_user.objects.filter(email=email).values())
    if len(users) != 1:
        return ""
    return users[0]['username']


def reset_password(request):
    try:
        key_ary = ['email']
        if mcm.check_keys(key_ary, request.POST) is False:
            return HttpResponse("wrong_email")
        email = request.POST['email']
        user_obj = tbl_user.objects.get(email=email)
        if user_obj is None:
            return HttpResponse("wrong_user")
        new_password = str(random.randint(100000, 999999))
        user_obj.s_password = new_password
        user_obj.set_password(new_password)
        user_obj.save()
        send_email_to_user([email], "Your password Reset", "Your new password is following;New password: " + new_password +
                           ";Please change your password after you sign in!", user_obj.username)
        return HttpResponse("success")
    except Exception as e:
        print('Reset password exception:' + str(e))
        return HttpResponse("none-registered-user")


def login(request):
    try:
        # time.sleep(1)
        key_ary = ['username', 'password']
        if mcm.check_keys(key_ary, request.POST) == False:
            return HttpResponse("fail")
        username = get_username(request.POST['username'])
        password = request.POST['password']
        if username == "":
            return HttpResponse("fail")
        if request.user.is_authenticated:
            request.session[mcm.encrypt('username')] = mcm.encrypt(username)
            return HttpResponse("profile")

        ret_code, user_obj = mcm.authenticate_user(username, password)

        if ret_code != AUTH_SUCCESS:
            return HttpResponse("fail")

        django_login(request, user_obj)

        request.session[mcm.encrypt('username')] = mcm.encrypt(username)
        request.session.save()
        return HttpResponse("profile")

    except Exception as e:
        return HttpResponse("fail")

def logout(request):
    django_logout(request)
    request.session.clear()
    return redirect('/')

@login_required
def subscription(request):
    plans = mcm.get_plans(request)
    data = {
        "menu_data": mcm.get_user_menu_data(),
        "menu_id": 2,
        "page_title": "Subscription",
        "basedata": mcm.get_user_data(request),
        "plans": plans,
        "client_id": mcm.get_paypal_client(request)
    }
    return render(request, 'user/subscription.html', data)

@login_required()
def profile(request):
    data = {
        "menu_data": mcm.get_user_menu_data(),
        "menu_id": 1,
        "page_title": "Profile",
        "basedata": mcm.get_user_data(request),
        "client_id": mcm.get_paypal_client(request)
    }
    return render(request, 'user/dashboard.html', data)

@login_required()
def order(request):
    user = mcm.get_user_data(request)
    user_order = list(tbl_order.objects.filter(userid=user['id']).values())
    order_cn = len(user_order)

    order_info = []
    orderno = 0
    copier_count = 0
    signal_count = 0
    for i in range(0, order_cn):
        if user_order[i]['subscription_deactived'] == 1:
            continue
        if datetime.now() > user_order[i]['expire_date']:
            continue

        plan_id = user_order[i]['plan_id']
        if plan_id != 12:
            copier_count += 1
        if plan_id > 11:
            signal_count += 1
        plan = tbl_plan.objects.get(pk=plan_id)
        if plan.period == 'C':
            account_count = user_order[i]['custom_account_cn']
        else:
            account_count = plan.account_count
        orderno += 1
        new_params = {}
        new_params['id'] = user_order[i]['id']
        new_params['plan_id'] = plan_id
        new_params['phone'] = user['phone']
        new_params['no'] = orderno
        new_params['create_date'] = user_order[i]['create_date']
        new_params['description'] = plan.description
        new_params['is_subscribed'] = 0
        if user_order[i]['subscription_id'] != '':
            new_params['is_subscribed'] = 1
            new_params['subscription_id'] = user_order[i]['subscription_id']
        new_params['plan_type'] = get_plan_type(plan.period)
        accounts_info = user_order[i]['account'].split(':')
        accounts = []
        for j in range(0, account_count):
            if j >= len(accounts_info):
                account_item = ''
            else:
                account_item = accounts_info[j]
            item = {"no": j+1, "name": "Account " + str(j+1), "account_item": account_item}
            accounts.append(item)

        new_params['accounts'] = accounts
        order_info.append(new_params)
    if copier_count > 0:
        apps = list(tbl_patch.objects.all().values())
        if len(apps) <= 0:
            app_path = ""
        else:
            app_path = apps[len(apps)-1]['url']
    else:
        app_path = ""
    data = {
        "menu_data": mcm.get_user_menu_data(),
        "menu_id": 4,
        "page_title": "Order",
        "basedata": user,
        "order_info": order_info,
        "order_cn": orderno,
        "app_path": app_path,
        "user_guide": mcs.user_guide_path,
        "copier_count": copier_count,
        "signal_count": signal_count,
        "client_id": mcm.get_paypal_client(request)
    }
    return render(request, 'user/orders.html', data)


def get_plan_type(period):
    if period == 'M':
        return "Monthly Plan"
    elif period == "Y":
        return "Yearly Plan"
    elif period == "L":
        return "Life Plan"
    elif period == "W":
        return "Trial Plan"
    elif period == "C":
        return "Custom Plan"

@login_required()
def load_paypal_regular_plans(request):
    params = request.POST
    plan_id = params['plan_id']
    try:
        plan = list(tbl_plan.objects.filter(pk=plan_id).values())[0]
    except:
        plan = {}
    data = {
        'plan': plan,
        'stripe_pubkey': mcm.get_stripe_key()['stripe_pubkey'],
        'payment': mcm.get_payment_enable()
    }
    if plan['period'] == 'L' or plan['period'] == 'W':
        return render(request, 'user/paypalonetime.html', data)
    else:
        return render(request, 'user/paypalrecurr.html', data)

@login_required()
def load_paypal_custom_plans(request):
    params = request.POST
    plan_type = params['plan_type']
    custom_account_cn = params['custom_account_cn']

    custom_plan_id = 0
    plans = list(tbl_plan.objects.all().values())
    for item in plans:
        if item['period'] == 'C':
            custom_plan_id = item['id']

    plan = {}
    plan['price'] = mcm.get_custom_price(request, plan_type, custom_account_cn)
    plan['id'] = custom_plan_id
    plan['custom_account_cn'] = custom_account_cn
    plan['plan_type'] = plan_type
    data = {
        'plan': plan,
        'stripe_pubkey': mcm.get_stripe_key()['stripe_pubkey'],
        'payment': mcm.get_payment_enable()
    }
    if plan_type == 'L':
        return render(request, 'user/paypalonetime_custom.html', data)
    else:
        return render(request, 'user/paypalrecurr_custom.html', data)

@login_required()
def cancel_prior_billing(request):
    user = mcm.get_user_data(request)
    user_order = list(tbl_order.objects.filter(userid=user['id']).values())
    is_ordered = 0
    subscription_id = ''
    if len(user_order) > 0:
        is_ordered = 1
        subscription_id = user_order[0]['subscription_id']

    if is_ordered and subscription_id != "":
        response = paypal_obj.Access_token().get_access_token()
        access_token = response.result.access_token
        reason = {"reason": "Service has to be updated"}
        subscription_response = paypal_obj.SubscriptionCancel().cancel_subscription(access_token, subscription_id, reason)
        if subscription_response.status_code != 204:
            return -1
    return 0

@login_required()
def cancel_subscription(request):
    try:
        params = request.POST
        oid = params['oid']
        sid = params['sid']
        response = paypal_obj.Access_token().get_access_token()
        access_token = response.result.access_token
        reason = {"reason": "Service has to be updated"}

        if "I-" in sid:
            subscription_response = paypal_obj.SubscriptionCancel().cancel_subscription(access_token, sid, reason)
            if subscription_response.status_code != 204:
                return HttpResponse('error')
        if "sub_" in sid:
            subscription_response = stripe.Subscription.delete(sid)
            if subscription_response.last_response.code >= 300:
                return HttpResponse('error')
        tbl_order.objects.filter(pk=int(oid)).update(subscription_deactived=1)
        try:
            send_email_to_user([mcs.ADMIN_EMAIL_ADDRESS], "Sorry to say about that",
                                "One paypal subscription has been deleted, subscription_id: " + str(sid))
        except Exception as e:
            print("cancel_subscription exception:" + str(e))
        return HttpResponse('success')
    except:
        return HttpResponse('error')

@login_required()
def create_paypal_plan(request):
    try:
        params = request.POST
        plan_id = params['plan_id']
        plan = tbl_plan.objects.get(pk=plan_id)
        plan_price = str(plan.price)

        if plan.period == 'M':
            recurr_period = "MONTH"
        if plan.period == "Y":
            recurr_period = "YEAR"
        response = paypal_obj.Access_token().get_access_token()
        access_token = response.result.access_token

        body_data = {'name': 'Telegram Copier',
                     'description': 'Telegram Copier Service (cost: $ ' + plan_price + ')',
                     'type': 'SERVICE',
                     'category': 'SOFTWARE'}
        response = paypal_obj.CatalogProduct().create_product(access_token, body_data)
        product_id = response.result.id

        body_data = {
            'product_id': product_id,
            'name': 'plan for service',
            'description': 'plan for Telegram Copier Service',
            'billing_cycles': [
                {"frequency": {"interval_unit": recurr_period, "interval_count": 1},
                 "tenure_type": "REGULAR",
                 "sequence": 1,
                 "total_cycles": 0,
                 "pricing_scheme": {"fixed_price": {"value": plan_price, "currency_code": "USD"}}}
            ],
            'payment_preferences': {
                "setup_fee_failure_action": "CONTINUE",
                "payment_failure_threshold": 3
            }
        }
        response = paypal_obj.BillingPlan().create_plan(access_token, body_data)
        paypal_plan_id = response.result.id
        return HttpResponse(paypal_plan_id)
    except:
        return HttpResponse('error')

@login_required()
def verify_paypal_subscription(request):
    try:
        params = request.POST
        plan_id = params['plan_id']
        data = json.loads(params['callback_data'])
        order_id = data['orderID']
        subscription_id = data['subscriptionID']
        user = mcm.get_user_data(request)
        new_params = {}
        new_params['userid'] = user['id']
        new_params['plan_id'] = int(plan_id)
        new_params['subscription_id'] = subscription_id
        new_params['create_date'] = datetime.now()
        new_params['expire_date'] = datetime.now() + timedelta(days=36500)
        plan = tbl_plan.objects.get(pk=int(plan_id))
        new_params['price'] = plan.price
        new_params['affiliate'] = user['affiliate']
        order_obj = tbl_order(**new_params)
        order_obj.save()
        try:
            send_email_to_user([mcs.ADMIN_EMAIL_ADDRESS], "Congratulation.",
                                "You got new paypal subscription, username: " + str(user['username']) + " sub_id: " + str(subscription_id) +
                                " plan_id: " + str(plan_id) + " plan_name: " + plan.name + " price: " + str(plan.price) + " affiliate: " + str(user['affiliate']))
        except Exception as e:
            print("paypal_subscription send_to_admin exception:" + str(e))
        return HttpResponse('success')
    except:
        return HttpResponse('error')

@login_required()
def verify_paypal_onepay(request):
    response_data = {}
    try:
        params = request.POST
        plan_id = params['plan_id']

        data = json.loads(params['data'])
        amount = json.loads(params['amount'])
        capture_id = params['capture_id']
        order_id = data['orderID']
        payer_id = data['payerID']
        amount_value = amount['value']
        amount_currency_code = amount['currency_code']

        paypal_response = paypal_order.GetOrder().get_order(order_id)
        response_amount_currency_code = paypal_response.result.purchase_units[0].amount.currency_code
        response_amount_value = paypal_response.result.purchase_units[0].amount.value

        if paypal_response.status_code == 200:
            if response_amount_currency_code != amount_currency_code:
                response_data['result'] = "error"
                response_data['content'] = "Currency Code Error"
                return HttpResponse(json.dumps(response_data))
            elif response_amount_value != amount_value:
                response_data['result'] = "error"
                response_data['content'] = "Amount Error"
                return HttpResponse(json.dumps(response_data))
            else:
                response = paypal_obj.Access_token().get_access_token()
                access_token = response.result.access_token
                capture_res = paypal_obj.Captures().get_captures(access_token, capture_id)
                user = mcm.get_user_data(request)
                new_params = {}
                new_params['userid'] = user['id']
                new_params['plan_id'] = int(plan_id)
                new_params['create_date'] = datetime.now()
                plan = tbl_plan.objects.get(pk=int(plan_id))
                new_params['price'] = response_amount_value
                new_params['affiliate'] = user['affiliate']
                if plan.period == 'W':
                    new_params['expire_date'] = datetime.now() + timedelta(days=7)
                else:
                    new_params['expire_date'] = datetime.now() + timedelta(days=36500)
                tbl_order_obj = tbl_order(**new_params)
                tbl_order_obj.save()
                success = {'amount': amount_value, 'result': 'success'}
                try:
                    send_email_to_user([mcs.ADMIN_EMAIL_ADDRESS], "Congratulation.",
                                        "You got new paypal one payment, username: " + str(
                                            user['username']) + " order_id: " + str(order_id) +
                                        " plan_id: " + str(plan_id) + " plan_name: " + plan.name + " price: " + str(
                                            plan.price) + " affiliate: " + str(user['affiliate']))
                except Exception as e:
                    print("paypal_onepayment send_to_admin exception:" + str(e))
                return HttpResponse(json.dumps(success))
        else:
            response_data['result'] = "error"
            response_data['content'] = "Status code Error, code:" + str(paypal_response.status_code)
            return HttpResponse(json.dumps(response_data))
    except Exception as e:
        response_data['result'] = "error"
        response_data['content'] = "Exception: " + str(e)
        return HttpResponse(json.dumps(response_data))

@login_required()
def update_account(request):
    try:
        params = request.POST
        plan_id = int(params['plan_id'])
        if plan_id != 12:
            order_id = params['orderid']
            accounts = params['accounts']
            accounts = json.loads(accounts)
            accountarray = []
            for key in accounts:
                if accounts[key] == '':
                    continue
                tmp = accounts[key].split(':')
                if len(tmp) > 1:
                    return HttpResponse('hacker')
                accountarray.append(accounts[key])
            accountstr = ":".join(accountarray)
            tbl_order.objects.filter(pk=int(order_id)).update(account=accountstr)
            return HttpResponse('success')
        if plan_id > 11:
            username = request.user.username
            phone = params['phone']
            if username == "":
                return HttpResponse('error')
            if params['phone'] == "":
                return HttpResponse('error')
            users = list(tbl_user.objects.filter(phone=phone).values())
            if len(users) > 1:
                return HttpResponse('duplicated')
            elif len(users) == 1:
                if users[0]['username'] != username:
                    return HttpResponse('duplicated')
                if users[0]['phone'] == phone:
                    return HttpResponse('success')
            tbl_user.objects.filter(username=username).update(phone=phone)
            return HttpResponse('success')
    except Exception as e:
        print("update_account exception:" + str(e))
        return HttpResponse('error')

@login_required()
def update_profile(request):
    try:
        params = request.POST
        user = mcm.get_user_data(request)
        userid = user['id']
        c_username = user['username']
        c_email = user['email']
        if c_username != params['username'] and tbl_user.objects.filter(username=params['username']).count() > 0:
            return HttpResponse("username_exist")
        if c_email != params['email'] and tbl_user.objects.filter(email=params['email']).count() > 0:
            return HttpResponse("email_exist")

        tbl_user.objects.filter(pk=userid).update(username=params['username'], email=params['email'])
        request.session[mcm.encrypt("username")] = mcm.encrypt(params["username"])
        return HttpResponse('success')
    except:
        return HttpResponse('error')

@login_required()
def update_password(request):
    try:
        params = request.POST
        password = params['password']
        user = mcm.get_user_data(request)
        if user['s_password'] != params['cur_password']:
            return HttpResponse('curpwdno')

        userid = user['id']
        user_obj = tbl_user.objects.get(pk=int(userid))
        user_obj.s_password = password
        user_obj.set_password(password)
        user_obj.save()

        return HttpResponse('success')
    except:
        return HttpResponse('error')

@login_required()
def check_current_plan(request):
    try:
        params = request.POST
        user = mcm.get_user_data(request)
        plan_id = params['plan_id']
        #check custome plan or not
        plan = tbl_plan.objects.get(pk=int(plan_id))
        if plan.period == 'W':
            if tbl_order.objects.filter(userid=user['id'], plan_id=int(plan_id)).count() > 0:
                return HttpResponse('trial_exist')
        if plan.period == 'C':
            custom_plan = 1
        else:
            custom_plan = 0

        custom_plan_info = list(tbl_custom_plan.objects.all().values())
        res = {'custom_plan': custom_plan, 'custom_plan_info': custom_plan_info}

        return HttpResponse(json.dumps(res))
    except:
        return HttpResponse('error')

@login_required()
def get_custom_plan_price(request, plan_type, count):
    try:
        total_price = mcm.get_custom_price(request, plan_type, count)
        return total_price
    except:
        return 0

@login_required()
def get_custom_plan_price(request):
    try:
        params = request.POST
        plan_type = params['plan_type']
        custom_account_cn = params['custom_account_cn']

        total_price = mcm.get_custom_price(request, plan_type, custom_account_cn)
        return HttpResponse(total_price)
    except:
        return HttpResponse(0)

@login_required()
def verify_paypal_onepay_custom(request):
    response_data = {}
    try:
        params = request.POST
        plan_id = params['plan_id']
        cac = params['cac']

        data = json.loads(params['data'])
        amount = json.loads(params['amount'])
        capture_id = params['capture_id']
        order_id = data['orderID']
        payer_id = data['payerID']
        amount_value = amount['value']
        amount_currency_code = amount['currency_code']

        paypal_response = paypal_order.GetOrder().get_order(order_id)
        response_amount_currency_code = paypal_response.result.purchase_units[0].amount.currency_code
        response_amount_value = paypal_response.result.purchase_units[0].amount.value

        if paypal_response.status_code == 200:
            if response_amount_currency_code != amount_currency_code:
                response_data['result'] = "error"
                response_data['content'] = "Currency Code Error"
                return HttpResponse(json.dumps(response_data))
            elif response_amount_value != amount_value:
                response_data['result'] = "error"
                response_data['content'] = "Amount Error"
                return HttpResponse(json.dumps(response_data))
            else:
                response = paypal_obj.Access_token().get_access_token()
                access_token = response.result.access_token
                capture_res = paypal_obj.Captures().get_captures(access_token, capture_id)
                # net_amount = capture_res.result.seller_receivable_breakdown.net_amount.value
                # paypal_fee = capture_res.result.seller_receivable_breakdown.paypal_fee.value
                # amount_value = float(net_amount)
                # paypal_fee = float(paypal_fee)

                user = mcm.get_user_data(request)
                new_params = {}
                new_params['userid'] = user['id']
                new_params['plan_id'] = int(plan_id)
                new_params['custom_account_cn'] = int(cac)
                new_params['create_date'] = datetime.now()
                new_params['expire_date'] = datetime.now() + timedelta(days=36500)
                new_params['price'] = response_amount_value
                new_params['affiliate'] = user['affiliate']
                new_params['custom_plan_type'] = params['plan_type']
                tbl_order_obj = tbl_order(**new_params)
                tbl_order_obj.save()
                try:
                    send_email_to_user([mcs.ADMIN_EMAIL_ADDRESS], "Congratulation.",
                                        "You got new paypal custom one payment, username: " + str(
                                            user['username']) + " order_id: " + str(order_id) +
                                        " plan_id: " + str(plan_id) + " plan_name: custom" + " price: " + str(
                                            amount_value) + " affiliate: " + str(user['affiliate']) + " accounts: " + str(cac))
                except Exception as e:
                    print("paypal_custom_onepayment send_to_admin exception:" + str(e))
                success = {'amount': amount_value, 'result': 'success'}
                return HttpResponse(json.dumps(success))
        else:
            response_data['result'] = "error"
            response_data['content'] = "Status code Error, code:" + str(paypal_response.status_code)
            return HttpResponse(json.dumps(response_data))
    except Exception as e:
        response_data['result'] = "error"
        response_data['content'] = "Exception: " + str(e)
        return HttpResponse(json.dumps(response_data))

@login_required()
def create_paypal_plan_custom(request):
    try:
        params = request.POST
        plan_type = params['plan_type']
        cac = int(params['cac'])
        plp = mcm.get_custom_price(request, plan_type, cac)

        if plan_type == 'M':
            recurr_period = "MONTH"
        if plan_type == "Y":
            recurr_period = "YEAR"
        response = paypal_obj.Access_token().get_access_token()
        access_token = response.result.access_token

        body_data = {'name': 'Telegram Copier',
                     'description': 'Telegram Copier Service (cost: $ ' + str(plp) + ')',
                     'type': 'SERVICE',
                     'category': 'SOFTWARE'}
        response = paypal_obj.CatalogProduct().create_product(access_token, body_data)
        product_id = response.result.id

        body_data = {
            'product_id': product_id,
            'name': 'plan for service',
            'description': 'plan for Telegram Copier Service',
            'billing_cycles': [
                {"frequency": {"interval_unit": recurr_period, "interval_count": 1},
                 "tenure_type": "REGULAR",
                 "sequence": 1,
                 "total_cycles": 0,
                 "pricing_scheme": {"fixed_price": {"value": str(plp), "currency_code": "USD"}}}
            ],
            'payment_preferences': {
                "setup_fee_failure_action": "CONTINUE",
                "payment_failure_threshold": 3
            }
        }
        response = paypal_obj.BillingPlan().create_plan(access_token, body_data)
        paypal_plan_id = response.result.id
        return HttpResponse(paypal_plan_id)
    except:
        return HttpResponse('error')

@login_required()
def verify_paypal_subscription_custom(request):
    try:
        params = request.POST
        plan_id = params['plan_id']
        cac = params['cac']

        data = json.loads(params['callback_data'])
        order_id = data['orderID']
        subscription_id = data['subscriptionID']
        user = mcm.get_user_data(request)

        new_params = {}
        new_params['userid'] = user['id']
        new_params['plan_id'] = int(plan_id)
        new_params['subscription_id'] = subscription_id
        new_params['custom_account_cn'] = int(cac)
        new_params['create_date'] = datetime.now()
        new_params['expire_date'] = datetime.now() + timedelta(days=36500)
        price = mcm.get_custom_price(request, params['plan_type'], int(cac))
        new_params['price'] = price
        new_params['affiliate'] = user['affiliate']
        new_params['custom_plan_type'] = params['plan_type']
        tbl_order_obj = tbl_order(**new_params)
        tbl_order_obj.save()
        try:
            send_email_to_user([mcs.ADMIN_EMAIL_ADDRESS], "Congratulation.",
                                "You got new paypal custom subscription payment, username: " + str(
                                    user['username']) + " order_id: " + str(subscription_id) +
                                " plan_id: " + str(plan_id) + " plan_name: custom" + " price: " + str(
                                    price) + " affiliate: " + str(user['affiliate']) + " accounts: " + str(cac))
        except Exception as e:
            print("paypal_custom_subscription send_to_admin exception:" + str(e))
        return HttpResponse('success')
    except:
        return HttpResponse('error')


@xframe_options_exempt
def handler403(request, exception):
    return render(request, 'error/http403.html', {}, status=403)

# ***********************************************************************************
# @Function: Send SMS Verification Code
# @Returns: Status Code
# -----------------------------------------------------------------------------------
def send_sv_code(account_sid, auth_token, dest_phonenumber):
    try:
        client = Client(account_sid, auth_token)
        service = client.verify.services.create(friendly_name='Vey')
        verification = client.verify.services(service.sid).verifications.create(to=dest_phonenumber, channel='sms')
        st_verify = verification.status
        return service.sid

    except Exception as e:
        try:
            if e.status == 429:
                return -2
            return -1
        except Exception:
            return -1


# ***********************************************************************************
# @Function: Check SMS Verification Code
# @Returns: Status Code TRUE/FALSE
# -----------------------------------------------------------------------------------
def check_sv_code(account_sid, auth_token, service_sid, dest_phonenumber, sms_code):
    try:
        client = Client(account_sid, auth_token)
        verification_check = client.verify.services(service_sid).verification_checks.create(to=dest_phonenumber, code=sms_code)
        if verification_check.status == 'approved':
            return True
        else:
            return False
    except Exception as e:
        return False


def robots(request):
    try:
        filepath = "static/telmtcp/text/robots.txt"
        filepath = os.path.join(settings.BASE_DIR, filepath)
        file = open(filepath, 'r')
        content = file.read()
        content = content.split('\n')
        file.close()
        new_params = {}
        new_params['title'] = mcs.site_title
        new_params['text'] = content
        return render(request, 'welcome/robots.html', new_params)
    except Exception as e:
        new_params = {}
        new_params['title'] = mcs.site_title
        new_params['text'] = "Sorry, something went wrong."
        return render(request, 'welcome/robots.html', new_params)


def sitemap(request):
    try:
        filepath = "static/telmtcp/text/sitemap.xml"
        filepath = os.path.join(settings.BASE_DIR, filepath)
        file = open(filepath, 'r')
        content = file.read()
        content = content.split('\n')
        file.close()
        new_params = {}
        new_params['title'] = mcs.site_title
        new_params['text'] = content
        return render(request, 'welcome/sitemap.html', new_params)
    except Exception as e:
        new_params = {}
        new_params['title'] = mcs.site_title
        new_params['text'] = "Sorry, something went wrong."
        return render(request, 'welcome/sitemap.html', new_params)

@login_required()
def verify_stripe_onepay(request):
    response_data = {}
    try:
        params = request.POST
        plan_id = params['plan_id']
        token = json.loads(params['token'])
        amount = params['amount']

        token_obj = stripe.Token.retrieve(token['id'])
        if token_obj.last_response.code >= 300:
            response_data['result'] = "error"
            response_data['content'] = "Status code Error, code:" + str(token_obj.last_response.code)
            return HttpResponse(json.dumps(response_data))
        if token_obj['card']['id'] == token['card']['id']:
            resp = stripe.Charge.create(amount=int(float(amount) * 100), currency="usd", card=token['id'],
                                        # source=token['id'],
                                        description="Add Funds")
            amount_value = float(amount)
            user = mcm.get_user_data(request)
            new_params = {}
            new_params['userid'] = user['id']
            new_params['plan_id'] = int(plan_id)
            new_params['create_date'] = datetime.now()
            new_params['price'] = amount_value
            new_params['affiliate'] = user['affiliate']
            plan = tbl_plan.objects.get(pk=int(plan_id))
            if plan.period == 'W':
                new_params['expire_date'] = datetime.now() + timedelta(days=7)
            else:
                new_params['expire_date'] = datetime.now() + timedelta(days=36500)
            tbl_order_obj = tbl_order(**new_params)
            tbl_order_obj.save()
            try:
                send_email_to_user([mcs.ADMIN_EMAIL_ADDRESS], "Congratulation.",
                                    "You got new stripe one payment, username: " + str(
                                        user['username']) + " plan_id: " + str(plan_id) + " plan_name: " + plan.name + " price: " + str(
                                        amount_value) + " affiliate: " + str(user['affiliate']))
            except Exception as e:
                print("stripe_onepayment send_to_admin exception:" + str(e))
            success = {'amount': amount_value, 'result': 'success'}
            return HttpResponse(json.dumps(success))
        else:
            response_data['result'] = "error"
            response_data['content'] = "Token error"
            return HttpResponse(json.dumps(response_data))
    except Exception as e:
        response_data['result'] = "error"
        response_data['content'] = "Exception: " + str(e)
        return HttpResponse(json.dumps(response_data))

@login_required()
def verifiy_stripe_subscription(request):
    try:
        params = request.POST
        plan_id = params['plan_id']
        plan = tbl_plan.objects.get(pk=plan_id)
        amount = str(plan.price)
        if plan.period == 'M':
            recurr_period = "month"
        if plan.period == "Y":
            recurr_period = "year"
        user = mcm.get_user_data(request)
        token = json.loads(params['token'])

        product_desp = 'Telegram Copier Service (cost: $ ' + str(amount) + ')'
        product_resp = stripe.Product.create(name="membership base service", type="service",
                                             description=product_desp)
        if product_resp.last_response.code >= 300:
            return HttpResponse("failure")
        plan_resp = stripe.Plan.create(amount=int(float(amount) * 100), currency="usd", interval=recurr_period,
                                       interval_count=1,
                                       product=product_resp['id'])
        if plan_resp.last_response.code >= 300:
            return HttpResponse("failure")
        customer = stripe.Customer.create(source=token['id'])
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{"plan": plan_resp['id']}],
        )
        new_params = {}
        new_params['userid'] = user['id']
        new_params['plan_id'] = int(plan_id)
        new_params['subscription_id'] = subscription['id']
        new_params['create_date'] = datetime.now()
        new_params['expire_date'] = datetime.now() + timedelta(days=36500)
        new_params['price'] = amount
        new_params['affiliate'] = user['affiliate']
        order_obj = tbl_order(**new_params)
        order_obj.save()
        try:
            send_email_to_user([mcs.ADMIN_EMAIL_ADDRESS], "Congratulation.",
                                "You got new stripe subscription payment, username: " + str(
                                    user['username']) + " plan_id: " + str(
                                    plan_id) + " plan_name: " + plan.name + " price: " + str(
                                    amount) + " affiliate: " + str(user['affiliate']))
        except Exception as e:
            print("stripe_subscription send_to_admin exception:" + str(e))
        return HttpResponse('success')
    except:
        return HttpResponse('error')

@login_required()
def verify_stripe_onepay_custom(request):
    response_data = {}
    try:
        params = request.POST
        plan_id = params['plan_id']
        token = json.loads(params['token'])
        amount = params['amount']
        cac = params['cac']

        token_obj = stripe.Token.retrieve(token['id'])
        if token_obj.last_response.code >= 300:
            response_data['result'] = "error"
            response_data['content'] = "Status code Error, code:" + str(token_obj.last_response.code)
            return HttpResponse(json.dumps(response_data))
        if token_obj['card']['id'] == token['card']['id']:
            resp = stripe.Charge.create(amount=int(float(amount) * 100), currency="usd", card=token['id'],
                                        # source=token['id'],
                                        description="Add Funds")
            amount_value = float(amount)
            user = mcm.get_user_data(request)
            new_params = {}
            new_params['userid'] = user['id']
            new_params['plan_id'] = int(plan_id)
            new_params['custom_account_cn'] = int(cac)
            new_params['create_date'] = datetime.now()
            new_params['expire_date'] = datetime.now() + timedelta(days=36500)
            new_params['price'] = amount_value
            new_params['affiliate'] = user['affiliate']
            new_params['custom_plan_type'] = params['plan_type']

            tbl_order_obj = tbl_order(**new_params)
            tbl_order_obj.save()
            try:
                send_email_to_user([mcs.ADMIN_EMAIL_ADDRESS], "Congratulation.",
                                    "You got new stripe custom one payment, username: " + str(
                                        user['username']) + " plan_id: " + str(
                                        plan_id) + " plan_name: custom_" + str(params['plan_type']) + " price: " + str(
                                        amount_value) + " affiliate: " + str(user['affiliate']) + " accounts: " + str(cac))
            except Exception as e:
                print("stripe_custom_onepayment send_to_admin exception:" + str(e))
            success = {'amount': amount_value, 'result': 'success'}
            return HttpResponse(json.dumps(success))
        else:
            response_data['result'] = "error"
            response_data['content'] = "Token error"
            return HttpResponse(json.dumps(response_data))
    except Exception as e:
        response_data['result'] = "error"
        response_data['content'] = "Exception: " + str(e)
        return HttpResponse(json.dumps(response_data))

@login_required()
def verifiy_stripe_subscription_custom(request):
    try:
        params = request.POST
        plan_id = params['plan_id']
        plan_type = params['plan_type']
        cac = int(params['cac'])
        plp = mcm.get_custom_price(request, plan_type, cac)

        if plan_type == 'M':
            recurr_period = "month"
        if plan_type == "Y":
            recurr_period = "year"

        plan = tbl_plan.objects.get(pk=plan_id)
        amount = str(plan.price)

        user = mcm.get_user_data(request)
        token = json.loads(params['token'])

        product_desp = 'Telegram Copier Service (cost: $ ' + str(plp) + ')'
        product_resp = stripe.Product.create(name="membership base service", type="service",
                                             description=product_desp)
        if product_resp.last_response.code >= 300:
            return HttpResponse("failure")
        plan_resp = stripe.Plan.create(amount=int(float(plp) * 100), currency="usd", interval=recurr_period,
                                       interval_count=1,
                                       product=product_resp['id'])
        if plan_resp.last_response.code >= 300:
            return HttpResponse("failure")
        customer = stripe.Customer.create(source=token['id'])
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{"plan": plan_resp['id']}],
        )
        new_params = {}
        new_params['userid'] = user['id']
        new_params['plan_id'] = int(plan_id)
        new_params['subscription_id'] = subscription['id']
        new_params['create_date'] = datetime.now()
        new_params['expire_date'] = datetime.now() + timedelta(days=36500)
        new_params['custom_plan_type'] = plan_type
        new_params['custom_account_cn'] = int(cac)
        new_params['price'] = plp
        new_params['affiliate'] = user['affiliate']
        order_obj = tbl_order(**new_params)
        order_obj.save()
        try:
            send_email_to_user([mcs.ADMIN_EMAIL_ADDRESS], "Congratulation.",
                                "You got new stripe custom subscription payment, username: " + str(
                                    user['username']) + " plan_id: " + str(
                                    plan_id) + " plan_name: custom_" + str(plan_type) + " price: " + str(
                                    plp) + " affiliate: " + str(user['affiliate']) + " accounts: " + str(cac))
        except Exception as e:
            print("stripe_custom_subscription send_to_admin exception:" + str(e))
        return HttpResponse('success')
    except:
        return HttpResponse('error')

def link(request):
    try:
        content = request.GET
        user = content['id']
        user = user.replace("space", " ")
        request.session['affiliate'] = user
    except:
        pass
    return HttpResponseRedirect('/')


@login_required()
def affiliate(request):
    user = mcm.get_user_data(request)
    user_order = list(tbl_order.objects.filter(affiliate=user['id']).values())
    order_cn = len(user_order)

    order_info = []
    orderno = 0
    total_price = 0
    for i in range(0, order_cn):
        plan_id = user_order[i]['plan_id']
        plan = tbl_plan.objects.get(pk=plan_id)
        create_date = user_order[i]['create_date']
        if create_date.year != datetime.now().year:
            continue
        if create_date.month != datetime.now().month:
            if plan.period != 'M' and (plan.period == 'C' and user_order[i]['custom_plan_type'] != 'M'):
                continue
            if user_order[i]['subscription_deactived'] == 1:
                continue
            if datetime.now() > user_order[i]['expire_date']:
                continue
            if user_order[i]['subscription_id'] == '':
                continue

        if user_order[i]['price'] <= 0:
            continue
        total_price += user_order[i]['price']
        user_name = mcm.get_user_name(user_order[i]['userid'])
        orderno += 1
        new_params = {}
        new_params['id'] = user_order[i]['id']
        new_params['no'] = orderno
        new_params['username'] = user_name
        new_params['price'] = user_order[i]['price']
        new_params['create_date'] = user_order[i]['create_date']
        new_params['expire_date'] = user_order[i]['expire_date']
        new_params['description'] = plan.description
        new_params['is_subscribed'] = 0
        if user_order[i]['subscription_id'] != '':
            new_params['is_subscribed'] = 1
            new_params['subscription_id'] = user_order[i]['subscription_id']
        new_params['plan_type'] = get_plan_type(plan.period)
        order_info.append(new_params)
    total_price = int(total_price)
    sharing_profit = total_price * mcs.affiliate_percent / 100
    sharing_profit = round(sharing_profit, 1)
    user_name = user['username'].replace(" ", "space")
    data = {
        "menu_data": mcm.get_user_menu_data(),
        "menu_id": 5,
        "page_title": "Affiliate",
        "basedata": user,
        "order_info": order_info,
        "order_cn": orderno,
        "total_price": total_price,
        "date": datetime.now(),
        "affiliate_link": mcs.affiliate_link + "?id=" + user_name,
        "affiliate_percent": mcs.affiliate_percent,
        "sharing_profit": sharing_profit,
        "client_id": mcm.get_paypal_client(request)
    }
    return render(request, 'user/affiliate.html', data)


@login_required()
def signal(request):
    user = mcm.get_user_data(request)
    plans = mcm.get_plans(request)
    data = {
        "menu_data": mcm.get_user_menu_data(),
        "menu_id": 3,
        "page_title": "Verified Signal",
        "basedata": user,
        "plans": plans,
        "client_id": mcm.get_paypal_client(request)
    }
    return render(request, 'user/signal.html', data)


@login_required()
def create_crypto_order(request):
    result = {'result': 'error'}
    try:
        content = request.POST
        plan_id = int(content['plan_id'])
        plan_type = content['plan_type']
        count = int(content['cac'])
        crypto = content['crypto']
        user = mcm.get_user_data(request)
        if plan_type != '' and count != 0:
            price = mcm.get_custom_price(request, plan_type, count)
        else:
            plan = tbl_plan.objects.get(pk=plan_id)
            price = plan.price
            plan_type = plan.period
            count = plan.account_count
        if price <= 0:
            result['content'] = 'price'
            return HttpResponse(json.dumps(result))
        if crypto == 'ETH':
            ex_price = my_ethereum.get_exchange_price()
            if ex_price <= 0:
                result['content'] = 'ex_price'
                return HttpResponse(json.dumps(result))
            eth_amount = price / ex_price
            gas_price = my_ethereum.get_gas_price()
            eth_limit = mcs.ETH_GAS_LIMIT * gas_price / pow(10, 9)
            if eth_limit <= 0:
                result['content'] = 'eth_limit'
                return HttpResponse(json.dumps(result))
            eth_amount += eth_limit
            eth_amount = round(eth_amount, 4)
            ex_price = round(price / eth_amount, 2)

            if user['eth_address'] == '' or user['eth_private'] == '':
                new_account = my_ethereum.create_wallet()
                private = new_account.privateKey.hex()
                tbl_user.objects.filter(pk=user['id']).update(eth_address=new_account.address, eth_private=private)
                user['eth_address'] = new_account.address
                user['eth_private'] = private
            if plan_type == 'M':
                delta = timedelta(days=30)
            elif plan_type == 'L':
                delta = timedelta(days=35600)
            elif plan_type == 'W':
                delta = timedelta(days=7)
            elif plan_type == 'Y':
                delta = timedelta(days=365)
            else:
                delta = timedelta(days=0)
            order_id = my_ethereum.create_wallet().address
            tbl_crypto_order.objects.filter(Q(user_id=user['id']) & Q(status=0)).update(status=-1)
            new_params = {'user_id': user['id'], 'crypto': crypto, 'address': user['eth_address'],
                          'private': user['eth_private'], 'plan_id': plan_id, 'create_date': datetime.now(),
                          'expire_date': datetime.now() + delta, 'custom_account_cn': count, 'amount': eth_amount,
                          'received': 0, 'price': price, 'custom_plan_type': plan_type, 'affiliate': user['affiliate'],
                          'ex_price': ex_price, 'gas_price': gas_price, 'status': 0, 'order_id': order_id}
            order_obj = tbl_crypto_order(**new_params)
            order_obj.save()
            result['result'] = 'success'
            result['crypto'] = crypto
            result['address'] = user['eth_address']
            result['plan_id'] = plan_id
            result['account_cn'] = count
            result['plan_type'] = plan_type
            result['ex_price'] = ex_price
            result['amount'] = eth_amount
            result['price'] = price
            result['expire'] = mcs.CRYPTO_TIMEOUT_ORDER
            result['order_id'] = order_id
            return HttpResponse(json.dumps(result))
        else:
            result['content'] = 'unknown crypto'
            return HttpResponse(json.dumps(result))
    except Exception as e:
        print(str(e))
        result['content'] = str(e)
        return HttpResponse(json.dumps(result))


@login_required()
def verify_crypto_order(request):
    try:
        content = request.GET
        order_id = content['order_id']
        order = list(tbl_crypto_order.objects.filter(order_id=order_id).values())[0]
        result = {'status': order['status'], 'received': order['received'], 'ref_code': order['ref_code'],
                  'ref_message': order['ref_message'], 'ref_tx': order['ref_tx'], 'refunded': order['refunded']}
        return HttpResponse(json.dumps(result))
    except Exception as e:
        print(str(e))
        result = {'status': 0}
        return HttpResponse(json.dumps(result))
