# # back-end/otp/tests.py
# from rest_framework.test import APITestCase
# from django.urls import reverse
# from otp.models import OTP
# from users.models import User
# from rest_framework_simplejwt.tokens import RefreshToken

# class OTPTests(APITestCase):
#     def test_request_and_verify_otp(self):
#         """
#         1. POST /api/otp/request_otp/ → creates an OTP record.
#         2. POST /api/otp/verify_otp/ with the code → returns JWT tokens.
#         """
#         phone = "+971501234567"
#         # 1. Request OTP
#         url = reverse('otp-request-otp')
#         resp = self.client.post(url, {'phone': phone}, format='json')
#         self.assertEqual(resp.status_code, 200)
#         otp_obj = OTP.objects.get(phone=phone)
#         self.assertFalse(otp_obj.is_verified)

#         # 2. Verify OTP
#         url = reverse('otp-verify-otp')
#         resp = self.client.post(url, {'phone': phone, 'code': otp_obj.code}, format='json')
#         self.assertEqual(resp.status_code, 200)
#         # Should include both access & refresh tokens
#         self.assertIn('access', resp.data)
#         self.assertIn('refresh', resp.data)
#         # OTP marked verified
#         otp_obj.refresh_from_db()
#         self.assertTrue(otp_obj.is_verified)

# class SalonSignupTests(APITestCase):
#     def test_salon_admin_signup_and_token_login(self):
#         """
#         1. POST /api/salon-signup/signup/ → creates User(role=ADMIN, is_active=False).
#         2. Admin must approve via is_approved=True.
#         3. POST /api/token/ with username/password → returns JWT.
#         """
#         url = reverse('salon-signup-signup')
#         data = {
#             'username': 'owner1',
#             'email': 'owner1@example.com',
#             'password': 'P@ssw0rd!'
#         }
#         resp = self.client.post(url, data, format='json')
#         self.assertEqual(resp.status_code, 201)
#         user = User.objects.get(username='owner1')
#         self.assertEqual(user.role, User.Roles.ADMIN)
#         self.assertFalse(user.is_active)

#         # Simulate admin approval
#         user.is_active = True
#         user.is_approved = True
#         user.save()

#         # Now attempt token login
#         url = reverse('token_obtain_pair')
#         resp = self.client.post(url, {'username': 'owner1', 'password': 'P@ssw0rd!'}, format='json')
#         self.assertEqual(resp.status_code, 200)
#         self.assertIn('access', resp.data)
#         self.assertIn('refresh', resp.data)