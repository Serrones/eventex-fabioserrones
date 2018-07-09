from django.core import mail
from django.test import TestCase
from eventex.subscriptions.forms import SubscriptionForm

class SubscriptionTest(TestCase):
    def setUp(self):
        self.resp = self.client.get('/inscricao/')


    def test_get(self):
        """GET / inscricao/ must return status code 200"""
        self.assertEqual(200, self.resp.status_code)


    def test_template(self):
        """Must use subscriptions/subscription_form.html"""
        self.assertTemplateUsed(self.resp, 'subscriptions/subscription_form.html')


    def test_html(self):
        """HTML must contain input tags"""
        self.assertContains(self.resp, '<form')
        self.assertContains(self.resp, '<input', 6)
        self.assertContains(self.resp, 'type="text"', 3)
        self.assertContains(self.resp, 'type="email"')
        self.assertContains(self.resp, 'type="submit"')


    def test_csrf(self):
        """HTML MUST contain csrf tag"""
        self.assertContains(self.resp, 'csrfmiddlewaretoken')


    def test_has_form(self):
        """Context MUST have subscription form"""
        form = self.resp.context['form']
        self.assertIsInstance(form, SubscriptionForm)


    def test_form_has_fields(self):
        """Form MUST have 4 fields"""
        form = self.resp.context['form']
        self.assertSequenceEqual(['nome', 'cpf', 'email', 'fone'],
                                  list(form.fields))


class SubscribePostTest(TestCase):
    def setUp(self):
        data = dict(nome="Fábio Serrão", cpf="12345678901",
                    email="fabioserrones@gmail.com", fone="11-99526-3577")
        self.resp = self.client.post('/inscricao/', data)
        self.email = mail.outbox[0]

    def test_post(self):
        """Valid post should redirect to /inscricao/"""
        self.assertEqual(302, self.resp.status_code)


    def test_send_subscribe_email(self):
        self.assertEqual(1, len(mail.outbox))


    def test_subscription_email_subject(self):
        expect = 'Confirmação de inscrição'
        self.assertEqual(expect, self.email.subject)


    def test_subscription_email_from(self):
        expect = 'contato@eventex.com.br'
        self.assertEqual(expect, self.email.from_email)


    def test_subscription_email_to(self):
        expect = ['contato@eventex.com.br', 'fabioserrones@gmail.com']
        self.assertEqual(expect, self.email.to)


    def test_subscription_email_body(self):
        self.assertIn('Fábio Serrão', self.email.body)
        self.assertIn('12345678901', self.email.body)
        self.assertIn('fabioserrones@gmail.com', self.email.body)
        self.assertIn('11-99526-3577', self.email.body)


class SubscribeInvalidPost(TestCase):
    def setUp(self):
        self.resp = self.client.post('/inscricao/', data={})


    def test_post(self):
        """Invalid POST should not redirect"""
        self.assertEqual(200, self.resp.status_code)


    def test_template(self):
        self.assertTemplateUsed(self.resp, 'subscriptions/subscription_form.html')


    def test_has_form(self):
        form = self.resp.context['form']
        self.assertIsInstance(form, SubscriptionForm)


    def test_form_has_errors(self):
        form = self.resp.context['form']
        self.assertTrue(form.errors)
