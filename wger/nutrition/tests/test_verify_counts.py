# Verification only (not part of the fix): prints the overview's query count
# for pages of 2, 10 and 20 ingredients.
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from wger.core.tests.base_testcase import WgerTestCase
from wger.nutrition.models import Ingredient


class PrintCounts(WgerTestCase):
    def test_print(self):
        self.user_login('admin')
        data = {
            'name': 'Test ingredient', 'language': 2, 'sodium': 10.54, 'energy': 176,
            'fat': 8.19, 'carbohydrates_sugar': 0.0, 'fat_saturated': 3.24, 'fiber': 0.0,
            'protein': 25.63, 'carbohydrates': 0.0, 'license': 1, 'license_author': 'internet',
        }
        for _ in range(30):
            self.client.post(reverse('nutrition:ingredient:add'), data)
        self.user_logout()
        url = reverse('nutrition:ingredient:list')
        ids = list(Ingredient.objects.filter(language=2).order_by('-id').values_list('id', flat=True))
        self.client.get(url)
        out = []
        for rows in (2, 10, 20):
            with CaptureQueriesContext(connection) as q:
                r = self.client.get(url, {'after': ids[rows]})
            out.append((len(r.context['ingredients_list']), len(q)))
        with CaptureQueriesContext(connection) as q:
            r = self.client.get(url)
        out.append(('first page', len(r.context['ingredients_list']), len(q)))
        print(f'\nVERIFYCOUNTS (rows, queries): {out}')
