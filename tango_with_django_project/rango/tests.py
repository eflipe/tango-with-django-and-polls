from django.test import TestCase
from rango.models import Category
from django.core.urlresolvers import reverse

# class CategoryMethodTests(TestCase):
#     def test_ensure_views_are_positive(self):
#     """
#     ensure_views_are_positive should results True for categories
# where views are zero or positive
#     """
#     cat = Category(name='test',  views=-1, likes=0)
#     cat.save()
#     self.asserEqual((cat.views >=0), True)
class IndexViewTests(TestCase):

    def test_index_view_with_no_categories(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('index'))
        self.asserEqual(response.status_code, 200)
        self.assertContains(response, "There are no categories present.")
        self.assertQuerysetEqual(response.context['categories'], [])

    def add_cat(name, views, likes):
        c = Category.objects.get_or_create(name=name)[0]
        c.views = views
        c.likes = likes
        c.save()
        return c

    def test_index_view_with_categories(self):
        """
        Check to make sure that the index has categories displayed
        """
        add_cat('test',1,1)
        add_cat('temp',1,1)
        add_cat('tmp',1,1)
        add_cat('tmp test temp',1,1)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "tmp test temp")
        num_cats =len(response.context['categories'])
        self.assertEqual(num_cats , 4)
