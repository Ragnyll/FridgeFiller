from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator

from lists.models import ShoppingList, UserProfile, Pantry, Item, ItemDetail, Party

from datetime import datetime
from datetime import timedelta

class HomePageView(TemplateView):
    """
    This view displays all the info being used on a users homepage
    """

    template_name = 'home/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)

        # get the most recently accessed list
        try:
            user = UserProfile.objects.get(user=self.request.user)
            owned_lists = ShoppingList.objects.filter(owners__in=[user])
            most_recent_list = owned_lists.order_by('-updated')
            most_recent_list = most_recent_list[0]
            user_party = Party.objects.get(owner=user)
            user_pantry = Pantry.objects.get(party=user_party)

            user_pantry_items = user_pantry.items.all()

            user_pantry_item_names = [x.name for x in user_pantry_items]

            context['user_pantry_items'] = user_pantry_items
            context['user_pantry_item_names'] = user_pantry_item_names
            context['user_pantry'] = user_pantry
            context['user_shopping_lists'] = ShoppingList.objects.filter(owners__in=[user])
            context['most_recent_list'] = most_recent_list
        except:
            pass

        # find expired and soon to expire items and add them to the context
        try:
            # these are all the items that are def expired
            expired_items = []
            # these are all the items that will expire in < 1 week
            warning_items = []

            user_party = Party.objects.get(name=user.name+"'s Personal Party")
            user_pantry = Pantry.objects.get(party=user_party)
            user_pantry_items = user_pantry.items.all()

            for item_detail in user_pantry_items:
                # a datetime object is constructed instead of using django datetime because django datetime is really strange and wont run timedeltas correctly
                datetime_expiration = datetime(item_detail.expiration_date.year, item_detail.expiration_date.month, item_detail.expiration_date.day, 0, 0)

                datetime_current = datetime.now()
                datetime_delta = datetime_expiration - datetime_current

                # see if item_detail is expired
                if datetime_delta.days < 1:
                    expired_items.append(item_detail)
                # see if item_detail will expire in less than a week
                elif datetime_delta.days <= 7 and datetime_delta.days >= 1:
                    warning_items.append(item_detail)

            # stick the two lists into the context dictionary
            context['expired_items'] = expired_items
            context['warning_items'] = warning_items
        except:
            pass

        # get the group's expired items
        try:
            user = UserProfile.objects.get(user=self.request.user)
            user_parties = Party.objects.filter(users__in=[user])
            personal_user_party = Party.objects.get(name=user.name+"'s Personal Party")
            user_parties = user_parties.exclude(name=user.name+"'s Personal Party")
            group_expired_items = []
            group_warning_items = []
            # add a line to remove he user personal party
            for party_i in user_parties:
                party_pantry = Pantry.objects.get(party=party_i)
                party_pantry_items = party_pantry.items.all()

                for item_detail in party_pantry_items:
                    # a datetime object is constructed instead of using django datetime because django datetime is really strange and wont run timedeltas correctly
                    datetime_expiration = datetime(item_detail.expiration_date.year, item_detail.expiration_date.month, item_detail.expiration_date.day, 0, 0)

                    datetime_current = datetime.now()
                    datetime_delta = datetime_expiration - datetime_current

                    # see if item_detail is expired
                    if datetime_delta.days < 1:
                        group_expired_items.append(item_detail)
                    # see if item_detail will expire in less than a week
                    elif datetime_delta.days <= 7 and datetime_delta.days >= 1:
                        group_warning_items.append(item_detail)

            context['group_expired_items'] = group_expired_items
            context['group_warning_items'] = group_warning_items

        except:
            pass

        return context
