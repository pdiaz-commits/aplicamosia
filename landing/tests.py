import json

from django.test import TestCase
from django.urls import reverse


class LandingPageTests(TestCase):
    def test_home_renders_business_proposition_and_packages(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AplicamosIA")
        self.assertContains(response, "Transformamos tu negocio con")
        self.assertContains(response, "IA avanzada")
        self.assertContains(response, "Piloto en 7 días")
        self.assertContains(response, "Agente comercial")
        self.assertContains(response, "Chat AplicamosIA")
        self.assertContains(response, "Privacidad y control humano")
        self.assertNotContains(response, "OCA-I")
        self.assertNotContains(response, "floWolf")
        self.assertNotContains(response, "Noktis")

    def test_home_exposes_accessible_primary_navigation(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, 'aria-label="Navegación principal"')
        self.assertContains(response, 'href="#paquetes"')
        self.assertContains(response, 'href="#chat"')
        self.assertContains(response, 'href="#contacto"')
        self.assertContains(response, "Saltar al contenido")


class ChatApiTests(TestCase):
    def test_chat_guides_first_reply(self):
        response = self.client.post(
            reverse("chat"),
            data=json.dumps({"message": "Tenemos una clínica", "history": []}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("reply", payload)
        self.assertFalse(payload["ready_for_lead"])
