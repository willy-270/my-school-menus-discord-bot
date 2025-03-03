from datetime import datetime
import json
import requests
from consts import DISTRICT_ID, LUNCH_MENU_ID, BREAKFAST_MENU_ID

class Meal:
    def __init__(self, desc: str, date: datetime, is_lunch: bool):
        self.desc = desc
        self.date = date
        self.is_lunch = is_lunch

class Month_Menu:
    def __init__(self, is_lunch: bool, date: datetime.date):
        self.is_lunch = is_lunch
        self.date = date
        self.menu_month_raw = self.get_month_raw(self.is_lunch)
        self.meals = self.get_meals()

    def get_meals(self):
        meals = []

        for entry in self.menu_month_raw:
            if entry is None:
                continue
            description = ''
            summary = ''
            recipe_count = 0
            category_count = 0
            try:
                for item in json.loads(entry['setting'])['current_display']:
                    if item['type'] == 'recipe' and recipe_count == 0:
                        recipe_count += 1
                        summary = f"Lunch: {item['name']}"
                    if item['type'] == 'category' and category_count == 0:
                        category_count += 1
                        description = f"{description}{item['name']}:\n"
                    elif item['type'] == 'category':
                        description = f"{description}\n{item['name']}:\n"
                    else:
                        description = f"{description}{item['name']}\n"
                if summary == '':
                    continue
            except KeyError:
                continue

            meal = Meal(description, datetime.fromisoformat(entry['day']).date(), self.is_lunch)
            meals.append(meal)
        
        return meals
    
    def get_month_raw(self, lucnh: bool):
        def get(district_id: int, site_id: int = None, menu_id: int = None, date: datetime.date = None) -> dict:
            url = f"https://myschoolmenus.com/api/organizations"

            if site_id:
                url += f"/{district_id}/sites/{site_id}"
            elif menu_id:
                url += f"/{district_id}/menus/{menu_id}"
                if date:
                    url += f"/year/{date.strftime('%Y')}/month/{date.strftime('%m')}/date_overwrites"

            r = requests.get(
                url=url,
                headers={'x-district': str(district_id)}
            )

            return r.json()

        if lucnh is True:
            menu = get(district_id = DISTRICT_ID, menu_id = LUNCH_MENU_ID, date = self.date)
        else:
            menu = get(district_id = DISTRICT_ID, menu_id = BREAKFAST_MENU_ID, date = self.date)

        menu_month_calendar = menu['data']
        return menu_month_calendar

def get_todays_meals(is_lunch: bool):
    return get_meal_by_date(datetime.now().date(), is_lunch)

def get_meal_by_date(date: datetime.date, is_lunch: bool) -> Meal | None:
    menu = Month_Menu(is_lunch, date)

    for meal in menu.meals:
        if meal.date == date:
            return meal
    
    return None

