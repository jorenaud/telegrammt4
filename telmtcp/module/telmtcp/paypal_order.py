from paypalcheckoutsdk.orders import OrdersGetRequest
from telmtcp.module.telmtcp.paypal_client import PayPalClient

class GetOrder(PayPalClient):
    # def __int__(self):
    #     self.client_id = "AeUTeSXjTVm2OicxNisW4HGsn17Gv19s-vwFmpfAQSJ37anM06FdM6KOzzEueGn6ZqKV2PUXCgwmxW49"
    #     self.client_secret = "EOW7dcxAQMku_djokMIBdEN-HpXCY5OiizOToW4XNEtPuv29C5TItZw1qNOvqGSS4L_SwemksWyDVNKv"
    #
    #     """Setting up and Returns PayPal SDK environment with PayPal Access credentials.
    #        For demo purpose, we are using SandboxEnvironment. In production this will be
    #        LiveEnvironment."""
    #     self.environment = SandboxEnvironment(client_id=self.client_id, client_secret=self.client_secret)
    #
    #     """ Returns PayPal HTTP client instance with environment which has access
    #         credentials context. This can be used invoke PayPal API's provided the
    #         credentials have the access to do so. """
    #     self.client = PayPalHttpClient(self.environment)


    def get_order(self, order_id):
        """Method to get order"""
        request = OrdersGetRequest(order_id)
        response = self.client.execute(request)

        return response


"""This is the driver function which invokes the get_order function with order id to retrieve
   an sample order. For the order id, we invoke the create order to create an new order and then we are using 
   the newly created order id for retrieving the order"""
if __name__ == '__main__':
    # createResponse = CreateOrder().create_order()
    # order = createResponse.result
    GetOrder().get_order(order.id)