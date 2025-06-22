import sys
import os
import json
import re
import ast
from openai import OpenAI

# Set Groq API key
os.environ["OPENAI_API_KEY"] = "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"

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["OPENAI_API_KEY"]
)

# Curated recipe database for common dishes as fallback
RECIPE_DATABASE = {
    "classic masala chai": {
        "title": "Classic Masala Chai",
        "serves": "2-3 cups",
        "ingredients": [
            "2 cups water",
            "1 cup whole milk",
            "2 tsp black tea leaves or 2 tea bags",
            "2-3 green cardamom pods, crushed",
            "1 inch fresh ginger, grated",
            "1 cinnamon stick",
            "2-3 cloves",
            "Sugar to taste"
        ],
        "toServe": [
            "Serve hot in small glasses or cups",
            "Pair with biscuits or snacks",
            "Garnish with a pinch of cardamom powder"
        ],
        "method": [
            "Boil water in a saucepan and add all the spices (cardamom, ginger, cinnamon, cloves)",
            "Let the spices simmer for 2-3 minutes to release their flavors",
            "Add tea leaves or tea bags and boil for 2 minutes until the color darkens",
            "Add milk and bring to a rolling boil, stirring occasionally",
            "Add sugar according to taste and boil for another minute",
            "Strain the chai through a fine mesh strainer into cups",
            "Serve immediately while hot and aromatic"
        ]
    },
    "veg samosa": {
        "title": "Veg Samosa",
        "serves": "Makes 15-20 samosas",
        "ingredients": [
            "2 cups all-purpose flour",
            "4 tbsp oil or ghee",
            "1/2 tsp salt",
            "Water as needed",
            "3 large potatoes, boiled and cubed",
            "1 cup green peas",
            "1 tsp cumin seeds",
            "1 tsp ginger-garlic paste",
            "2 green chilies, chopped",
            "1 tsp turmeric powder",
            "1 tsp red chili powder",
            "1 tsp garam masala",
            "Fresh coriander leaves",
            "Salt to taste",
            "Oil for deep frying"
        ],
        "toServe": [
            "Serve hot with mint chutney",
            "Pair with tamarind chutney",
            "Enjoy with hot tea"
        ],
        "method": [
            "Make dough by mixing flour, 2 tbsp oil, salt and water. Knead until smooth and rest for 30 minutes",
            "Heat oil in a pan, add cumin seeds and let them splutter",
            "Add ginger-garlic paste and green chilies, sauté for a minute",
            "Add boiled potatoes, peas, and all spices. Mix well and cook for 5-7 minutes",
            "Add fresh coriander and let the filling cool completely",
            "Divide dough into small balls and roll each into an oval shape",
            "Cut each oval in half and form a cone, fill with potato mixture",
            "Seal the edges with water and ensure no filling spills out",
            "Heat oil for deep frying and fry samosas until golden brown and crispy",
            "Drain on paper towels and serve hot with chutneys"
        ]
    },
    "paneer butter masala": {
        "title": "Paneer Butter Masala",
        "serves": "4 people",
        "ingredients": [
            "400g paneer, cubed",
            "2 large tomatoes, chopped",
            "1 large onion, chopped",
            "1 tbsp ginger-garlic paste",
            "2 tbsp butter",
            "1 tbsp oil",
            "1 tsp cumin seeds",
            "1 bay leaf",
            "1/2 cup heavy cream",
            "1 tsp red chili powder",
            "1/2 tsp turmeric powder",
            "1 tsp garam masala",
            "1 tsp kasuri methi",
            "Salt to taste",
            "Fresh coriander for garnish"
        ],
        "toServe": [
            "Serve hot with naan or roti",
            "Pair with basmati rice",
            "Garnish with fresh cream"
        ],
        "method": [
            "Heat butter and oil in a heavy-bottomed pan",
            "Add cumin seeds and bay leaf, let them splutter",
            "Add chopped onions and sauté until golden brown",
            "Add ginger-garlic paste and cook for 2 minutes",
            "Add chopped tomatoes and cook until they break down completely",
            "Add all dry spices and cook for 2-3 minutes",
            "Blend the mixture into a smooth paste and strain back into the pan",
            "Add cream and bring to a gentle simmer",
            "Add paneer cubes gently and simmer for 5-7 minutes",
            "Sprinkle kasuri methi and garam masala, garnish with coriander and serve"
        ]
    }
}

def validate_recipe_quality(recipe):
    """Validate that recipe doesn't contain placeholder values and has proper content"""
    if not isinstance(recipe, dict):
        return False
    
    required_keys = ["title", "serves", "ingredients", "toServe", "method"]
    if not all(key in recipe for key in required_keys):
        return False
    
    placeholder_patterns = [
        r'sample', r'placeholder', r'example', r'test', r'dummy',
        r'dish\s*name', r'recipe\s*name', r'title\s*here',
        r'^\.\.\.$', r'^sample$', r'^example$', r'^placeholder$'
    ]
    
    # Check title
    title = str(recipe.get("title", "")).lower().strip()
    if len(title) < 3 or any(re.search(pattern, title) for pattern in placeholder_patterns):
        return False
    
    # Check serves
    serves = str(recipe.get("serves", "")).lower().strip()
    if len(serves) < 1 or any(re.search(pattern, serves) for pattern in placeholder_patterns):
        return False
    
    # Check ingredients
    ingredients = recipe.get("ingredients", [])
    if not isinstance(ingredients, list) or len(ingredients) < 3:
        return False
    
    for ingredient in ingredients:
        ingredient_str = str(ingredient).lower().strip()
        if len(ingredient_str) < 3 or any(re.search(pattern, ingredient_str) for pattern in placeholder_patterns):
            return False
    
    # Check method
    method = recipe.get("method", [])
    if not isinstance(method, list) or len(method) < 3:
        return False
    
    for step in method:
        step_str = str(step).lower().strip()
        if len(step_str) < 10 or any(re.search(pattern, step_str) for pattern in placeholder_patterns):
            return False
    
    return True

def get_fallback_recipe(dish_name):
    """Get contextually appropriate fallback recipe"""
    dish_lower = dish_name.lower().strip()
    
    # Direct match from database
    if dish_lower in RECIPE_DATABASE:
        return RECIPE_DATABASE[dish_lower]
    
    # Fuzzy matching for common variations
    for key, recipe in RECIPE_DATABASE.items():
        if any(word in dish_lower for word in key.split()):
            # Customize title to match requested dish
            customized_recipe = recipe.copy()
            customized_recipe["title"] = dish_name.title()
            return customized_recipe
    
    # Category-based fallback
    if any(word in dish_lower for word in ["chai", "tea"]):
        return RECIPE_DATABASE["classic masala chai"]
    elif any(word in dish_lower for word in ["samosa", "snack"]):
        return RECIPE_DATABASE["veg samosa"]
    elif any(word in dish_lower for word in ["paneer", "curry"]):
        return RECIPE_DATABASE["paneer butter masala"]
    
    # Generic Indian dish fallback
    return {
        "title": dish_name.title(),
        "serves": "4 people",
        "ingredients": [
            "Main ingredient as per dish requirement",
            "Onions, chopped",
            "Tomatoes, chopped",
            "Ginger-garlic paste",
            "Basic Indian spices (turmeric, red chili powder, garam masala)",
            "Oil or ghee",
            "Salt to taste",
            "Fresh coriander for garnish"
        ],
        "toServe": [
            "Serve hot with rice or Indian bread",
            "Garnish with fresh coriander",
            "Pair with pickle or yogurt"
        ],
        "method": [
            "Prepare all ingredients by washing, chopping, and measuring them properly",
            "Heat oil or ghee in a heavy-bottomed pan over medium heat",
            "Add whole spices if using and let them release their aroma",
            "Add chopped onions and sauté until golden brown and fragrant",
            "Add ginger-garlic paste and cook until the raw smell disappears",
            "Add tomatoes and cook until they break down and form a thick base",
            "Add main ingredient and mix well with the masala base",
            "Add powdered spices and salt, cook until flavors blend well",
            "Simmer covered until the dish is cooked through and flavors develop",
            "Garnish with fresh coriander and serve hot"
        ]
    }

def clean_recipe_data(recipe):
    """Clean and standardize recipe data"""
    cleaned = {}
    
    # Clean title
    cleaned["title"] = str(recipe.get("title", "")).strip().title()
    if not cleaned["title"]:
        cleaned["title"] = "Indian Dish"
    
    # Clean serves
    cleaned["serves"] = str(recipe.get("serves", "")).strip()
    if not cleaned["serves"]:
        cleaned["serves"] = "4 people"
    
    # Clean ingredients
    ingredients = recipe.get("ingredients", [])
    cleaned["ingredients"] = []
    for ingredient in ingredients:
        clean_ingredient = str(ingredient).strip()
        if clean_ingredient and len(clean_ingredient) > 2:
            cleaned["ingredients"].append(clean_ingredient)
    
    if len(cleaned["ingredients"]) < 3:
        cleaned["ingredients"] = ["Basic ingredients as per recipe requirement"]
    
    # Clean toServe
    to_serve = recipe.get("toServe", [])
    cleaned["toServe"] = []
    for item in to_serve:
        clean_item = str(item).strip()
        if clean_item and len(clean_item) > 2:
            cleaned["toServe"].append(clean_item)
    
    if not cleaned["toServe"]:
        cleaned["toServe"] = ["Serve hot", "Garnish as desired"]
    
    # Clean method
    method = recipe.get("method", [])
    cleaned["method"] = []
    for step in method:
        clean_step = str(step).strip()
        if clean_step and len(clean_step) > 5:
            cleaned["method"].append(clean_step)
    
    if len(cleaned["method"]) < 3:
        cleaned["method"] = [
            "Prepare all ingredients properly",
            "Cook according to traditional method",
            "Serve hot when ready"
        ]
    
    return cleaned

# Validate input
if len(sys.argv) != 2:
    print(json.dumps({"error": "Expected 1 argument: dish name"}))
    sys.exit(1)

dish = sys.argv[1].strip()

# Enhanced prompt with better instructions and examples
prompt = f"""Create a complete, authentic Indian recipe for "{dish}". Provide detailed, practical instructions that anyone can follow.

REQUIREMENTS:
- Use authentic Indian cooking methods and ingredients
- Include precise measurements and cooking times
- Write clear, step-by-step instructions
- Use ingredients commonly available in Indian markets
- Make portions suitable for home cooking

FORMAT (return ONLY this JSON structure):
{{
  "title": "{dish}",
  "serves": "number of people or portions",
  "ingredients": ["ingredient 1 with quantity", "ingredient 2 with quantity", ...],
  "toServe": ["serving suggestion 1", "serving suggestion 2", ...],
  "method": ["detailed step 1", "detailed step 2", ...]
}}

EXAMPLES OF GOOD CONTENT:
- Ingredients: "2 cups basmati rice", "1 tsp turmeric powder", "500g chicken, cut into pieces"
- Method steps: "Heat 2 tbsp oil in a heavy-bottomed pan over medium heat", "Add cumin seeds and let them splutter for 30 seconds"
- Serving: "Serve hot with mint chutney", "Garnish with fresh coriander leaves"

IMPORTANT: 
- Never use placeholder text like "sample", "example", or "..."
- Each method step should be detailed with timing and techniques
- Include traditional Indian cooking methods
- Use double quotes only in JSON
- Return valid JSON without extra text"""

# Try multiple attempts to get good recipe
max_attempts = 3
parsed = None

for attempt in range(max_attempts):
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert Indian chef who creates detailed, authentic recipes. Return ONLY valid JSON with complete recipe information. Never use placeholder values."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3 + (attempt * 0.1),
            max_tokens=1000
        )
        
        raw_output = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        match = re.search(r'{.*}', raw_output, re.DOTALL)
        json_str = match.group() if match else raw_output
        
        # Parse JSON
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError:
            try:
                parsed = ast.literal_eval(json_str)
            except Exception:
                continue
        
        # Validate the recipe
        if validate_recipe_quality(parsed):
            break
        else:
            parsed = None
            
    except Exception as e:
        continue

# Use fallback if all attempts failed
if not parsed:
    parsed = get_fallback_recipe(dish)

# Clean and validate final output
final_recipe = clean_recipe_data(parsed)

# Final quality check - use guaranteed fallback if still invalid
if not validate_recipe_quality(final_recipe):
    final_recipe = get_fallback_recipe(dish)

# Output clean JSON
print(json.dumps(final_recipe, ensure_ascii=False))



 # import sys
# # import os
# # import json
# # import re
# # import ast
# # from openai import OpenAI

# # # Set Groq API key
# # os.environ["OPENAI_API_KEY"] = "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"  # Replace with your actual key

# # client = OpenAI(
# #     base_url="https://api.groq.com/openai/v1",
# #     api_key=os.environ["OPENAI_API_KEY"]
# # )

# # # Validate argument
# # if len(sys.argv) != 2:
# #     print(json.dumps({ "error": "Expected 1 argument: dish name" }))
# #     sys.exit(1)

# # dish = sys.argv[1].strip()

# # # Prompt to generate recipe
# # prompt = (
# #     f"Give a complete, detailed Indian-style recipe for '{dish}'. Include:\n"
# #     "- title (same as dish name)\n"
# #     "- serves (as a number or short string)\n"
# #     "- a list of ingredients (simple, widely available)\n"
# #     "- a list of optional items or 'to serve'\n"
# #     "- step-by-step method (detailed and clear)\n"
# #     "Respond ONLY with a JSON object in the format:\n"
# #     "{\n"
# #     "  \"title\": \"Dish Name\",\n"
# #     "  \"serves\": \"4\",\n"
# #     "  \"ingredients\": [\"...\", \"...\"],\n"
# #     "  \"toServe\": [\"...\", \"...\"],\n"
# #     "  \"method\": [\"...\", \"...\"],\n"
# #     "}\n"
# #     "Use double quotes only. Return valid JSON. Do not include extra text or explanation."
# # )

# # # Call LLM
# # response = client.chat.completions.create(
# #     model="llama3-70b-8192",
# #     messages=[
# #         {"role": "system", "content": "You are a helpful recipe assistant that only outputs valid JSON."},
# #         {"role": "user", "content": prompt}
# #     ],
# #     temperature=0.4,
# #     max_tokens=800
# # )

# # # Extract text response
# # raw_output = response.choices[0].message.content.strip()

# # # Extract JSON
# # match = re.search(r'{.*}', raw_output, re.DOTALL)
# # json_str = match.group() if match else raw_output

# # # Parse JSON safely
# # def parse_json(data):
# #     try:
# #         return json.loads(data)
# #     except json.JSONDecodeError:
# #         try:
# #             return ast.literal_eval(data)
# #         except Exception:
# #             return None

# # parsed = parse_json(json_str)

# # # Validate and clean
# # if isinstance(parsed, dict) and all(k in parsed for k in ["title", "serves", "ingredients", "toServe", "method", "imageUrl"]):
# #     print(json.dumps(parsed, ensure_ascii=False))
# # else:
# #     print(json.dumps({ "error": "Invalid JSON format or missing keys", "raw": raw_output }))
# # import sys
# # import os
# # import json
# # import re
# # import ast
# # from openai import OpenAI

# # # Set Groq API key
# # os.environ["OPENAI_API_KEY"] = "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"

# # client = OpenAI(
# #     base_url="https://api.groq.com/openai/v1",
# #     api_key=os.environ["OPENAI_API_KEY"]
# # )

# # # ✅ Fallback template
# # DEFAULT_RECIPE = {
# #     "title": "Sample",
# #     "serves": "Sample",
# #     "ingredients": [
# #         "Sample"
# #     ],
# #     "toServe": [
# #         "Sample"
# #     ],
# #     "method": [
# #         "Sample"
# #     ]
# # }

# # # Validate argument
# # if len(sys.argv) != 2:
# #     print(json.dumps({"error": "Expected 1 argument: dish name"}))
# #     sys.exit(1)

# # dish = sys.argv[1].strip()

# # # Prompt for the LLM
# # prompt = (
# #     f"Give a complete, detailed Indian-style recipe for '{dish}'. Include:\n"
# #     "- title (same as dish name)\n"
# #     "- serves (as a number or short string)\n"
# #     "- a list of ingredients (simple, widely available)\n"
# #     "- a list of optional items or 'to serve'\n"
# #     "- step-by-step method (detailed and clear)\n"
# #     "- imageUrl (just a link, placeholder okay)\n"
# #     "Respond ONLY with a JSON object in the format:\n"
# #     "{\n"
# #     "  \"title\": \"Dish Name\",\n"
# #     "  \"serves\": \"4\",\n"
# #     "  \"ingredients\": [\"...\", \"...\"],\n"
# #     "  \"toServe\": [\"...\", \"...\"],\n"
# #     "  \"method\": [\"...\", \"...\"],\n"
# #     "}\n"
# #     "Use double quotes only. Return valid JSON. Do not include extra text or explanation."
# #     "Replace every placeholder value in the array below with real Indian dishes, tags, and descriptions. Do NOT return any value like 'Sample'."
# # )


# # # Query Groq
# # response = client.chat.completions.create(
# #     model="llama3-70b-8192",
# #     messages=[
# #         {"role": "system", "content": "You are a helpful recipe assistant that only outputs valid JSON."},
# #         {"role": "user", "content": prompt}
# #     ],
# #     temperature=0.4,
# #     max_tokens=800
# # )

# # # Extract raw output
# # raw_output = response.choices[0].message.content.strip()

# # # Extract JSON from response
# # match = re.search(r'{.*}', raw_output, re.DOTALL)
# # json_str = match.group() if match else raw_output

# # # Safe parser
# # def parse_json(data):
# #     try:
# #         return json.loads(data)
# #     except json.JSONDecodeError:
# #         try:
# #             return ast.literal_eval(data)
# #         except Exception:
# #             return None

# # parsed = parse_json(json_str)

# # # Check if valid recipe structure
# # required_keys = ["title", "serves", "ingredients", "toServe", "method"]
# # is_valid = isinstance(parsed, dict) and all(k in parsed and parsed[k] for k in required_keys)

# # # Output flat valid JSON (either real or fallback)
# # final_recipe = parsed if is_valid else DEFAULT_RECIPE
# # print(json.dumps(final_recipe, ensure_ascii=False))

# import sys
# import os
# import json
# import re
# import ast
# from openai import OpenAI

# # Set Groq API key
# os.environ["OPENAI_API_KEY"] = "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"

# client = OpenAI(
#     base_url="https://api.groq.com/openai/v1",
#     api_key=os.environ["OPENAI_API_KEY"]
# )

# # ✅ Safe fallback recipe with real values
# DEFAULT_RECIPE = {
#     "title": "sample",
#     "serves": "sample",
#     "ingredients": [
#         "sample"
#     ],
#     "toServe": [
#         "sample"
#     ],
#     "method": [
#         "sample"
#     ]
# }

# # Validate input
# if len(sys.argv) != 2:
#     print(json.dumps({"error": "Expected 1 argument: dish name"}))
#     sys.exit(1)

# dish = sys.argv[1].strip()

# # 🔥 Updated prompt (no imageUrl)
# prompt = (
#     f"Give a complete, detailed Indian-style recipe for '{dish}'. Include:\n"
#     "- title (same as dish name)\n"
#     "- serves (as a number or short string)\n"
#     "- a list of ingredients (simple, widely available)\n"
#     "- a list of optional items or 'to serve'\n"
#     "- step-by-step method (detailed and clear)\n"
#     "Respond ONLY with a JSON object in the format:\n"
#     "{\n"
#     "  \"title\": \"Dish Name\",\n"
#     "  \"serves\": \"4\",\n"
#     "  \"ingredients\": [\"...\", \"...\"],\n"
#     "  \"toServe\": [\"...\", \"...\"],\n"
#     "  \"method\": [\"...\", \"...\"]\n"
#     "}\n"
#     "Use double quotes only. Do not include any extra text or explanations."
#     "Replace all values in this array with appropriate dishes. Return the same array, structure unchanged."
#     "Replace every placeholder value in the array below with real Indian dishes, tags, and descriptions. Do NOT return any value like 'title': 'sample'."
# )

# # Query LLM
# response = client.chat.completions.create(
#     model="llama3-70b-8192",
#     messages=[
#         {"role": "system", "content": "You are a helpful recipe assistant who knows the recipes of all the dishes that only outputs valid JSON."},
#         {"role": "user", "content": prompt}
#     ],
#     temperature=0.4,
#     max_tokens=800
# )

# # Parse response
# raw_output = response.choices[0].message.content.strip()
# match = re.search(r'{.*}', raw_output, re.DOTALL)
# json_str = match.group() if match else raw_output

# # Safe JSON parsing
# def parse_json(data):
#     try:
#         return json.loads(data)
#     except json.JSONDecodeError:
#         try:
#             return ast.literal_eval(data)
#         except Exception:
#             return None

# parsed = parse_json(json_str)

# # Validate recipe
# required_keys = ["title", "serves", "ingredients", "toServe", "method"]
# is_valid = isinstance(parsed, dict) and all(k in parsed and parsed[k] for k in required_keys)

# # Output final recipe
# final_recipe = parsed if is_valid else DEFAULT_RECIPE
# print(json.dumps(final_recipe, ensure_ascii=False))
