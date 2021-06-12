import sys
from sty import fg, bg, ef, rs
from telmtcp.module.telmtcp import constant as mcs
from telmtcp.database.orm.models import *
from telmtcp.module.glb.ret_code import *
from django.contrib.auth import authenticate
import threading
import smtplib
from email.message import EmailMessage
import email.utils
from datetime import datetime
import os


def print_exception():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    error_msg = bg.red
    error_msg += str(exc_obj) + ", File: " + str(exc_tb.tb_frame.f_code.co_filename) + ", Line: " + str(exc_tb.tb_lineno)
    error_msg += bg.rs
    print(error_msg)


def encrypt(text):
    return text

def decrypt(text):
    return text


def get_mail_account(noreply=True):
    mail_account = {}
    if noreply:
        mail_account["email"] = "noreply@telegrammt4.com"
        mail_account["password"] = "ZAQ!XSW@cde3"
    else:
        if mcs.SERVICE_EMAIL_INDEX == 0:
            mail_account["email"] = "service@telegrammt4.com"
            mcs.SERVICE_EMAIL_INDEX = 1
        else:
            mail_account["email"] = "tech@telegrammt4.com"
            mcs.SERVICE_EMAIL_INDEX = 0
        mail_account["password"] = "ZAQ!XSW@cde3"
    return mail_account


def send_mail_thread(to_emails, subject, message):
    th = threading.Thread(target=send_mail, args=(to_emails, subject, message))
    th.start()


def send_mail(to_email, subject, message, server='mail20.mymailcheap.com', port=587, noreply=True):
    try:
        mail_account = get_mail_account(noreply)
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = mail_account["email"]
        msg['To'] = ', '.join(to_email)
        msg['Date'] = email.utils.formatdate(timeval=None, localtime=False, usegmt=False)
        msg.set_content(message)
        # print(msg)
        server = smtplib.SMTP(server, port)
        # server.set_debuglevel(1)  # set debug level
        server.starttls()
        server.login(mail_account["email"], mail_account["password"])  # username & password
        server.send_message(msg)
        server.quit()
        print('Successfully sent the mail.')
        return 0
    except:
        return -1


def check_keys(key_ary, dict_obj):
    for key in key_ary:
        if key not in dict_obj:
            return False
    return True

def authenticate_user(username, password):
    try:
        user_obj_list = list(tbl_user.objects.filter(username=username))
        if len(user_obj_list) == 0:
            return AUTH_ACCOUNT_NOT_FOUND, None
        user_obj = user_obj_list[0]
        if user_obj.is_active == 0:
            return AUTH_ACCOUNT_DISABLED, None

        user = authenticate(username=username, password=password)
        if user == None:
            return AUTH_WRONG_PWD, None

        return AUTH_SUCCESS, user

    except Exception as e:
        return AUTH_UNKOWN_ERROR, None

def get_user_menu_data():
    user_menu_data = [
        {
            'id': 1,
            'url': 'profile',
            'name': 'My Profile',
            'icon': 'fa fa-dashboard',
            'parent': 0,
            'has_child': 0
        },
        {
            'id': 2,
            'url': 'subscription',
            'name': 'Copier Plans',
            'icon': 'fa fa-telegram',
            'parent': 0,
            'has_child': 0
        },
        {
            'id': 3,
            'url': 'signal',
            'name': 'Verified Signal',
            'icon': 'fa fa-signal',
            'parent': 0,
            'has_child': 0
        },
        {
            'id': 4,
            'url': 'order',
            'name': 'My Orders',
            'icon': 'fa fa-list-ul',
            'parent': 0,
            'has_child': 0
        },
        {
            'id': 5,
            'url': 'affiliate',
            'name': 'My Affiliate',
            'icon': 'fa fa-users',
            'parent': 0,
            'has_child': 0
        }
    ]
    return user_menu_data


def get_user_name(user_id):
    try:
        user_obj = list(tbl_user.objects.filter(id=user_id).values())[0]
        return user_obj['username']
    except:
        return ''


def get_user_id(username):
    try:
        user_obj = list(tbl_user.objects.filter(username=username).values())[0]
        return user_obj['id']
    except:
        return 0


def get_user_data(request):
    username = request.user.username
    try:
        user_obj = list(tbl_user.objects.filter(username=username).values())[0]
    except:
        user_obj = {}
    return user_obj


def get_plans(request):
    plans = list(tbl_plan.objects.all().values())
    plan_dict = {}
    for plan in plans:
        plan_key = 'plan_' + str(plan['id'])
        plan_dict[plan_key] = plan
    return plan_dict


def get_custom_price(request, plan_type, account_cn):
    custom_plan_info = list(tbl_custom_plan.objects.all().values())
    price = 0
    for item in custom_plan_info:
        if plan_type == item['type']:
            price = item['price']

    price = round(float(price) * int(account_cn), 2)
    return price

def get_paypal_client(request):
    if mcs.MODE == 'L':
        return mcs.PayPal_Client
    else:
        return mcs.PayPal_Sandbox_Client

def get_stripe_key():
    if mcs.MODE == 'L':
        return {"stripe_client_secret_key": mcs.Stripe_Api_Secret, "stripe_pubkey": mcs.Stripe_Api_key}
    else:
        return {"stripe_client_secret_key": mcs.Stripe_Test_Api_Secret, "stripe_pubkey": mcs.Stripe_Test_Api_key}


def get_payment_enable():
    return mcs.PAYMENT_ENABLE


def print_log(message, caption="DEBUG", log_level=1):
    try:
        if log_level < mcs.LOG_LEVEL:
            return
        buffer = str(message)
        log = "[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] " + caption + ": " + buffer + "\n"
        if mcs.PRINT_ENABLE:
            print(log)
        if mcs.LOG_ENABLE is False:
            return
        orig = mcs.LOG_FILE_PATH + mcs.LOF_FILE_NAME
        if not os.path.exists(mcs.LOG_FILE_PATH):
            os.makedirs(mcs.LOG_FILE_PATH)
        if os.path.exists(orig):
            size = os.path.getsize(orig)
            if size > mcs.LOG_MAX_SIZE * 1000:
                os.remove(orig)
        file = open(orig, 'a')
        file.writelines(log)
        file.close()
    except Exception as e:
        print(str(e))
