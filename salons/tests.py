# # back-end/salons/tests.py
# from rest_framework.test import APITestCase
# from users.models import User
# from salons.models import Salon
# from django.urls import reverse

# class RBACSalonTests(APITestCase):
#     def setUp(self):
#         # Create a customer and a salon-admin
#         self.cust = User.objects.create_user(username='cust', password='pass', role=User.Roles.CUSTOMER, is_active=True)
#         self.owner = User.objects.create_user(username='owner', password='pass', role=User.Roles.ADMIN, is_active=True, is_approved=True)

#     def get_token(self, user):
#         resp = self.client.post(reverse('token_obtain_pair'),
#                                 {'username':user.username,'password':'pass'}, format='json')
#         return resp.data['access']

#     def test_customer_cannot_create_salon(self):
#         token = self.get_token(self.cust)
#         self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
#         resp = self.client.post(reverse('salon-list'), {'name':'X','phone':'123'}, format='json')
#         self.assertEqual(resp.status_code, 403)  # Forbidden

#     def test_admin_can_create_salon(self):
#         token = self.get_token(self.owner)
#         self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
#         resp = self.client.post(reverse('salon-list'), {'name':'MySalon','phone':'0501234567'}, format='json')
#         self.assertEqual(resp.status_code, 201)
#         self.assertTrue(Salon.objects.filter(name='MySalon').exists())
