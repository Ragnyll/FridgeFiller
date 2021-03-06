
import sys
import logging
import os

file_path = __file__

app_loc = os.path.dirname(os.path.dirname(os.path.abspath(file_path)))
sys.path.append(app_loc)
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fridgefiller.settings")
django.setup()



from django.contrib.auth.models import User
from django.utils import timezone
from lists.models import UserProfile, Party, ShoppingList, Pantry, Item, ItemDetail

import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)

logger.setLevel(logging.DEBUG)

# pre: The database is empty
# post: fills up the database with model entries
def generate_db():
    codex_u, created = User.objects.get_or_create(username="codex", first_name="Cyd")
    if created:
        logger.debug("Created codex user")
    else:
        logger.debug("Did no create codex user")
        logger.debug("Codex username %s" % codex_u.username)
        
    zaboo_u, created = User.objects.get_or_create(username="zaboo", first_name="Sujan")
    tink_u, created = User.objects.get_or_create(username="tinkerballa", first_name="April")
    vork_u, created = User.objects.get_or_create(username="vork", first_name="Herman")
    bladezz_u, created = User.objects.get_or_create(username="bladezz", first_name="Simon")
    clara_u, created = User.objects.get_or_create(username="clara", first_name="clara")

    users = [codex_u, zaboo_u, tink_u, vork_u, bladezz_u, clara_u]

    codex_up = UserProfile.objects.get(name="codex")
    codex_up.description = "timid, priest"
    
    zaboo_up = UserProfile.objects.get(name="zaboo")
    zaboo_up.description = "annoying, warlock"
    
    tink_up = UserProfile.objects.get(name="tinkerballa")
    tink_up.description = "entitled, ranger"
    
    vork_up = UserProfile.objects.get(name="vork")
    vork_up.description = "cheap and pendantic, warrior"
    
    bladezz_up = UserProfile.objects.get(name="bladezz")
    bladezz_up.description = "immature, rogue"
    
    clara_up = UserProfile.objects.get(name="clara")
    clara_up.description = "mother, mage"
    
    user_profiles = [codex_up, zaboo_up, tink_up, vork_up, bladezz_up, clara_up]
    for i in user_profiles:
        i.save()
    
    p = Party.objects.create(name="Knights Of Good", owner=vork_up)
    p.owner = vork_up
    for i in [codex_up, zaboo_up, tink_up, bladezz_up, clara_up]:
        p.users.add(i)

    shoplist = ShoppingList.objects.create(name="Raid Potions")
    
    shoplist.description = "potion list for molten core"
    
    pots = [Item.objects.create(name="Elixir of Mighty Agility", description="Increases agility by 25 for 1 hour"),
            Item.objects.create(name="Elixir of Mighty Defenese", description="Increases armor by 180 for 1 hour"),
            Item.objects.create(name="Fel Strength", description="Increases attack power by 90 for 1 hour")]
    
    for i in pots:
        i.save()
        shoplist.items.add(i)

    for i in user_profiles:
        shoplist.owners.add(i)

    shoplist.save()


    pot_details = [ItemDetail.objects.create(name=pots[0].name, description=pots[0].description,
                                             cost="100", barcode="1032231", unit="oz", amount=20,
                                             last_purchased=timezone.now(),
                                             expiration_date=timezone.now()),
                   ItemDetail.objects.create(name=pots[1].name, description=pots[1].description,
                                             cost="100", barcode="3242312", unit="oz", amount=30,
                                             last_purchased=timezone.now(),
                                             expiration_date=timezone.now()),
                   ItemDetail.objects.create(name=pots[2].name, description=pots[2].description,
                                             cost="30", barcode="2332413", unit="oz", amount=1,
                                             last_purchased=timezone.now(),
                                             expiration_date=timezone.now())]

    guild_bank = Pantry.objects.create(party=p, description="guild bank")
    for i in pot_details:
        guild_bank.items.add(i)
        i.save()

    guild_bank.save()



    fruit_list = [Item.objects.create(name="Orange", description="orange"),
                  Item.objects.create(name="Banana", description="yellow made for holding"),
                  Item.objects.create(name="Green Apple", description="Sour")]

    codex_shop_list = ShoppingList.objects.create(name="Codex Fruit list")
    for i in fruit_list:
        codex_shop_list.items.add(i)
    codex_shop_list.owners.add(codex_up)


if __name__ == "__main__":
    generate_db()
