from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView, UpdateView, View
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator

from .models import *
import walmart_api as wapi

def disp_info(request):
    users = UserProfile.objects.all()
    parties = Party.objects.all()
    shoppinglists = ShoppingList.objects.all()

    return render(request, 'lists/disp_info.html',{'users': users})


class ListsView(TemplateView):
    """
    This view displays all shopping lists that a user owns
    """
    template_name = "lists/lists.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """
        Ensures that only authenticated users can access the view.
        """
        return super(ListsView, self).dispatch(request, *args, **kwargs)
    

    def get_context_data(self, **kwargs):
        context = super(ListsView, self).get_context_data(**kwargs)

        user = UserProfile.objects.get(user=self.request.user)
        
        context['user_shopping_lists'] = ShoppingList.objects.filter(owners__in=[user])
        
        return context
    
    
class ListView(TemplateView):
    """
    This view displays a singular list with id <list_id> and the items in that list
    """
    template_name = "lists/list.html"


class NewListView(TemplateView):
    """
    This view lets a user add new items to a list, and submit that tentative list as a new list object
    """
    template_name = "lists/new_list.html"


class EditListView(TemplateView):
    """
    This view lets a user edit a list with id <list_id>

    Similar to NewListView, but it will show the items already in the list, and allow for more items to be added, whereas NewListView is blank
    """
    template_name = "lists/edit_list.html"


class PantryView(TemplateView):
    """
    This view displays the user's pantry
    """
    template_name = "lists/pantry.html"


    def get_context_data(self, **kwargs):
        context = super(PantryView, self).get_context_data(**kwargs)

        user = UserProfile.objects.get(user=self.request.user)
        
        party = Party.objects.filter(owner=user)[0]
        pantry = Pantry.objects.filter(party=party)[0]

        context['party'] = party
        context['pantry'] = pantry
        context['pantry_items'] = pantry.items.all()
        return context


class NewItemView(View):
    """
    This view adds a new item to a list, and returns the user to the lists page
    """
    def post(self, request, *args, **kwargs):
        item_name = request.POST.get('new-item-name', False)
        item_desc = request.POST.get('new-item-description', False)
        
        list_id = request.POST.get('list-id', False)
        list_obj = ShoppingList.objects.get(id=list_id)

        # Don't make empty items!
        if item_name == "":
            messages.add_message(request, messages.ERROR, "<span class='alert alert-danger'>ERROR: You must provide a name for the item.</span>", extra_tags=int(list_id))            
            return redirect('/lists')
        
        # Get or create item in database
        try:
            new_item, created = Item.objects.get_or_create(name=item_name, description=item_desc)
        except:
            messages.add_message(request, messages.ERROR, "<span class='alert alert-danger'>Error: can't create or get that item.</span>", extra_tags=int(list_id))
            return redirect('/lists')

        # Don't add duplicate items
        if new_item in list_obj.items.all():
            messages.add_message(request, messages.ERROR, "<span class='alert alert-danger'>That item already exists in the list.</span>", extra_tags=int(list_id))
            return redirect('/lists')

        # Add item to list
        try:
            list_obj.items.add(new_item)
            list_obj.save()
            messages.add_message(request, messages.SUCCESS, "<span class='alert alert-success'>Success!  Added " + item_name + " to list!</span>", extra_tags=int(list_id))
        except:
            messages.add_message(request, messages.ERROR, "<span class='alert alert-danger'>Unable to add " + item_name + " to list.</span>", extra_tags=int(list_id))

        return redirect('/lists/#' + list_id)

class RemoveItemFromListView(View):
    """
    This view removes an item from a list and returns the user to their lists page
    """

    def post(self, request, *args, **kwargs):
        item_name = request.POST.get('remove-item-name', False)
        item_desc = request.POST.get('remove-item-description', False)
        list_id = request.POST.get('list-id', False)

        item_obj = Item.objects.get(name=item_name, description=item_desc)
        list_obj = ShoppingList.objects.get(id=list_id)
        
        # Remove the item from the list
        try:
            list_obj.items.remove(item_obj)
            messages.add_message(request, messages.SUCCESS, "<span class='alert alert-success'>Successfully removed " + item_name + " from list</span>", extra_tags=int(list_id))
        except:
            messages.add_message(request, messages.ERROR, "<span class='alert alert-danger'>Unable to remove " + item_name + " from list.</span>", extra_tags=int(list_id))

        return redirect("/lists")


def item_detail(request, *args, **kwargs):
    items = wapi.item_search(request.GET.get('item-name', False))
    return JsonResponse({'items': items})

def upc(request, *args, **kwargs):
    items = wapi.upc_search(request.GET.get('upc', False))
    return JsonResponse({'items': items})

class test(TemplateView):
    template_name = "lists/test.html"    
