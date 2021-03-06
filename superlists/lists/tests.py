from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from views import home_page
from models import Item,List

# Create your tests here.

class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        expected_html = render_to_string('home.html')
        request = HttpRequest()
        
        response = home_page(request)
        
        self.assertEqual(response.content.decode(), expected_html)
        
class ListAndItemModelTest(TestCase):
    def test_saving_and_retrieving_items(self):
        list_ = List()
        list_.save()
        
        first_item = Item()
        first_item.text = 'The first (ever) list item'
        first_item.list = list_
        first_item.save()
        
        second_item = Item()
        second_item.text = 'Item the Second'
        second_item.list = list_
        second_item.save()
        
        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)

        saved_items = Item.objects.all()
        self.assertAlmostEqual(saved_items.count(), 2)
        
        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text,'The first (ever) list item')
        self.assertEqual(first_saved_item.list,list_)
        self.assertEqual(second_saved_item.text,'Item the Second')
        self.assertEqual(second_saved_item.list,list_)

class ListViewTest(TestCase):

    def test_display_all_items(self):
        list_ = List.objects.create()
        Item.objects.create(text='Item 1', list=list_)
        Item.objects.create(text='Item 2', list=list_)
        
    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get('/lists/%d/' % (list_.id,))
        self.assertTemplateUsed(response, 'list.html')
        
    def test_display_only_items_for_that_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text='Item 1', list=correct_list)
        Item.objects.create(text='Item 2', list=correct_list)
        other_list = List.objects.create()
        Item.objects.create(text='Item 3', list=other_list)
        Item.objects.create(text='Item 4', list=other_list)

        response = self.client.get('/lists/%d/' % (correct_list.id,))
        self.assertContains( response, 'Item 1')
        self.assertContains( response, 'Item 2')
        self.assertNotContains( response, 'Item 3')
        self.assertNotContains( response, 'Item 4')
        
    def test_home_page_displays_all_list_items(self):
        list_ = List.objects.create()
        Item.objects.create(text='Item 1', list=list_)
        Item.objects.create(text='Item 2', list=list_)

        response = self.client.get('/lists/%d/' % list_.id)
        
        self.assertContains( response, 'Item 1')
        self.assertContains( response, 'Item 2')

    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get('/lists/%d/' % (correct_list.id,))
        self.assertEqual(response.context['list'], correct_list)

class NewListTest(TestCase):

    def test_home_page_can_save_a_POST_request(self):
        self.client.post('/lists/new', data={'item_text':'A new list item'})
        
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual( new_item.text, 'A new list item')
        
    def test_home_page_redirects_after_POST(self):
        response = self.client.post('/lists/new', data={'item_text':'A new list item'})
        
        self.assertEqual(response.status_code, 302)
        new_list = List.objects.first()
        self.assertRedirects(response, '/lists/%d/' % new_list.id)
        

class NewItemTest(TestCase):
    def test_can_save_a_POST_to_an_existing_list(self):
        list_1 = List.objects.create()
        list_2 = List.objects.create()
        
        self.client.post('/lists/%d/add_item' % (list_1.id,), 
                         data={'item_text' : 'New item for list_1'})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual( new_item.text, 'New item for list_1')
        self.assertEqual( new_item.list, list_1)

    def test_redirects_to_list_view(self):
        list_1 = List.objects.create()
        list_2 = List.objects.create()

        response = self.client.post('/lists/%d/add_item' % (list_1.id,), 
                         data={'item_text' : 'New item for list_1'})
        
        self.assertRedirects(response, '/lists/%d/' % list_1.id )
        