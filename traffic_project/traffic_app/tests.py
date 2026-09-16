from django.test import TestCase
from .forms import RegisterForm


class RegisterFormTests(TestCase):
	def test_numeric_only_username_is_rejected(self):
		form = RegisterForm(data={
			'username': '123456',
			'email': 'user@example.com',
			'password1': 'StrongPassword123!',
			'password2': 'StrongPassword123!',
		})

		self.assertFalse(form.is_valid())
		self.assertIn('Username cannot contain only numbers.', form.errors['username'])

	def test_username_with_letters_is_accepted(self):
		form = RegisterForm(data={
			'username': 'user123',
			'email': 'user@example.com',
			'password1': 'StrongPassword123!',
			'password2': 'StrongPassword123!',
		})

		self.assertTrue(form.is_valid())

# Create your tests here.
