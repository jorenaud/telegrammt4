from telmtcp.module.telmtcp.paypal_client import PayPalClient
from paypalcheckoutsdk.core import AccessTokenRequest
from paypalrestsdk import BillingPlan
import braintreehttp
try:
    from urllib import quote  # Python 2.X
except ImportError:
    from urllib.parse import quote  # Python 3+

class Access_token(PayPalClient):
    def get_access_token(self):
        request = AccessTokenRequest(self.environment)
        response = self.client.execute(request)
        return response


class CatalogProductRequest:
    def __init__(self, access_token, request_body_data):
        self.path = "/v1/catalogs/products"
        self.verb = "POST"
        self.body = request_body_data

        self.headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {0}".format(access_token)
                }

class CatalogProduct(PayPalClient):
    def create_product(self, access_token, body_data):
        request = CatalogProductRequest(access_token, body_data)
        response = self.client.execute(request)
        return response

class PlanRequest:
    def __init__(self, access_token, request_body_data):
        self.path = "/v1/billing/plans"
        self.verb = "POST"
        self.body = request_body_data

        self.headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {0}".format(access_token)
                }

class BillingPlan(PayPalClient):
    def create_plan(self, access_token, body_data):
        request = PlanRequest(access_token, body_data)
        response = self.client.execute(request)
        return response

class SubscriptionRequest:
    def __init__(self, access_token, subscription_id):
        self.path = "/v1/billing/subscriptions/{subscription_id}?".replace("{subscription_id}", quote(str(subscription_id)))
        self.verb = "GET"
        self.headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {0}".format(access_token)
        }

class Subscription(PayPalClient):
    def get_subscription(self, access_token, subscription_id):
        request = SubscriptionRequest(access_token, subscription_id)
        response = self.client.execute(request)
        return response

class SubscriptionCancelRequest:
    def __init__(self, access_token, subscription_id, body_data):
        self.path = "/v1/billing/subscriptions/{subscription_id}/cancel".replace("{subscription_id}", quote(str(subscription_id)))
        self.verb = "POST"
        self.headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {0}".format(access_token)
        }
        self.body = body_data

class SubscriptionCancel(PayPalClient):
    def cancel_subscription(self, access_token, subscription_id, body_data):
        request = SubscriptionCancelRequest(access_token, subscription_id, body_data)
        response = self.client.execute(request)
        return response

class CapturesRequest:
    def __init__(self, access_token, capture_id):
        self.path = "/v2/payments/captures/{capture_id}?".replace("{capture_id}", quote(str(capture_id)))
        self.verb = "GET"
        self.headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {0}".format(access_token)
        }

class Captures(PayPalClient):
    def get_captures(self, access_token, capture_id):
        request = CapturesRequest(access_token, capture_id)
        response = self.client.execute(request)
        return response