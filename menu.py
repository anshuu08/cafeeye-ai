# menu.py - CafeEye Restaurant Menu

MENU = {
    "veg": [
        {
            "id": "V1",
            "name": "Paneer Butter Masala",
            "price": 280,
            "calories": 420,
            "spice": "Medium",
            "description": "Creamy tomato gravy with soft paneer cubes"
        },
        {
            "id": "V2",
            "name": "Dal Makhani",
            "price": 220,
            "calories": 380,
            "spice": "Mild",
            "description": "Slow cooked black lentils in buttery gravy"
        },
        {
            "id": "V3",
            "name": "Veg Biryani",
            "price": 260,
            "calories": 520,
            "spice": "Medium",
            "description": "Fragrant basmati rice with mixed vegetables"
        },
        {
            "id": "V4",
            "name": "Palak Paneer",
            "price": 260,
            "calories": 350,
            "spice": "Mild",
            "description": "Fresh spinach gravy with cottage cheese"
        },
        {
            "id": "V5",
            "name": "Mushroom Masala",
            "price": 240,
            "calories": 290,
            "spice": "Hot",
            "description": "Spicy mushrooms in onion tomato gravy"
        },
        {
            "id": "V6",
            "name": "Veg Manchurian",
            "price": 200,
            "calories": 310,
            "spice": "Medium",
            "description": "Crispy vegetable balls in Indo-Chinese sauce"
        },
        {
            "id": "V7",
            "name": "Masala Dosa",
            "price": 180,
            "calories": 340,
            "spice": "Mild",
            "description": "Crispy rice crepe with spiced potato filling"
        },
        {
            "id": "V8",
            "name": "Veg Fried Rice",
            "price": 200,
            "calories": 450,
            "spice": "Mild",
            "description": "Wok tossed rice with fresh vegetables"
        },
    ],
    "nonveg": [
        {
            "id": "N1",
            "name": "Butter Chicken",
            "price": 340,
            "calories": 520,
            "spice": "Mild",
            "description": "Tender chicken in rich buttery tomato sauce"
        },
        {
            "id": "N2",
            "name": "Chicken Biryani",
            "price": 320,
            "calories": 650,
            "spice": "Medium",
            "description": "Aromatic basmati rice layered with spiced chicken"
        },
        {
            "id": "N3",
            "name": "Mutton Rogan Josh",
            "price": 420,
            "calories": 580,
            "spice": "Hot",
            "description": "Slow cooked mutton in Kashmiri spices"
        },
        {
            "id": "N4",
            "name": "Chicken 65",
            "price": 280,
            "calories": 420,
            "spice": "Hot",
            "description": "Crispy spicy fried chicken — South Indian style"
        },
        {
            "id": "N5",
            "name": "Fish Curry",
            "price": 360,
            "calories": 480,
            "spice": "Medium",
            "description": "Fresh fish in tangy coconut gravy"
        },
        {
            "id": "N6",
            "name": "Prawn Masala",
            "price": 400,
            "calories": 390,
            "spice": "Hot",
            "description": "Juicy prawns in spicy onion masala"
        },
        {
            "id": "N7",
            "name": "Egg Fried Rice",
            "price": 220,
            "calories": 480,
            "spice": "Mild",
            "description": "Wok fried rice with scrambled eggs"
        },
        {
            "id": "N8",
            "name": "Chicken Noodles",
            "price": 260,
            "calories": 520,
            "spice": "Medium",
            "description": "Stir fried noodles with chicken and vegetables"
        },
    ]
}

def get_menu_text():
    """Get full menu as text for AI context"""
    text = "RESTAURANT MENU:\n\n"
    text += "VEG DISHES:\n"
    for item in MENU["veg"]:
        text += f"- {item['id']}: {item['name']} | Rs.{item['price']} | {item['calories']} cal | Spice: {item['spice']}\n"
    text += "\nNON-VEG DISHES:\n"
    for item in MENU["nonveg"]:
        text += f"- {item['id']}: {item['name']} | Rs.{item['price']} | {item['calories']} cal | Spice: {item['spice']}\n"
    return text

def get_spice_emoji(spice):
    return {"Mild": "🟢", "Medium": "🟡", "Hot": "🔴"}.get(spice, "⚪")