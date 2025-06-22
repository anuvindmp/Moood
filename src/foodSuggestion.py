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

# Curated fallback dishes based on common Indian preferences
FALLBACK_DISHES = [
    {"dish": "classic masala chai", "tag": "Comfort Drink", "desc": "Aromatic spiced tea perfect for any mood and weather"},
    {"dish": "veg samosa", "tag": "Popular Snack", "desc": "Crispy pastry filled with spiced potatoes and peas"},
    {"dish": "chicken biriyani", "tag": "Main Course", "desc": "Fragrant basmati rice with tender chicken and aromatic spices"},
    {"dish": "paneer butter masala", "tag": "Vegetarian", "desc": "Rich and creamy curry with soft cottage cheese cubes"},
    {"dish": "classic dosa", "tag": "South Indian", "desc": "Crispy fermented crepe served with coconut chutney and sambar"},
    {"dish": "mango lassi", "tag": "Refreshing Drink", "desc": "Creamy yogurt-based drink with sweet mango flavor"}
]

def validate_dish_quality(dishes):
    """Validate that dishes don't contain placeholder values and are proper Indian dishes"""
    placeholder_patterns = [
        r'dish\s*\d+', r'tag\s*\d+', r'description\s*\d+',
        r'placeholder', r'example', r'sample', r'test',
        r'^dish$', r'^tag$', r'^desc$', r'^description$'
    ]
    
    for dish in dishes:
        dish_name = dish.get("dish", "").lower().strip()
        tag = dish.get("tag", "").lower().strip()
        desc = dish.get("desc", "").lower().strip()
        
        # Check for placeholder patterns
        for pattern in placeholder_patterns:
            if re.search(pattern, dish_name) or re.search(pattern, tag) or re.search(pattern, desc):
                return False
        
        # Check for empty or too short values
        if len(dish_name) < 3 or len(tag) < 3 or len(desc) < 10:
            return False
    
    return True

def get_contextual_fallback(mood, temp_c, hunger, craving, veg):
    """Generate contextually appropriate fallback dishes"""
    contextual_dishes = []
    
    # Based on temperature
    if int(temp_c) > 30:  # Hot weather
        contextual_dishes.extend([
            {"dish": "fresh lime water", "tag": "Cooling Drink", "desc": "Refreshing citrus drink to beat the heat"},
            {"dish": "vanilla ice cream", "tag": "Cold Dessert", "desc": "Creamy frozen dessert perfect for hot weather"},
            {"dish": "mint chaas", "tag": "Cooling Drink", "desc": "Spiced buttermilk with fresh mint and cumin"}
        ])
    else:  # Moderate/cool weather
        contextual_dishes.extend([
            {"dish": "hot masala chai", "tag": "Warm Drink", "desc": "Spiced tea to warm you up"},
            {"dish": "aloo paratha", "tag": "Comfort Food", "desc": "Stuffed flatbread with spiced potato filling"}
        ])
    
    # Based on hunger level
    if hunger.lower() == "snack":
        contextual_dishes.extend([
            {"dish": "masala peanuts", "tag": "Crunchy Snack", "desc": "Spiced roasted peanuts for light munching"},
            {"dish": "bhel puri", "tag": "Street Food", "desc": "Tangy puffed rice snack with chutneys"}
        ])
    else:
        contextual_dishes.extend([
            {"dish": "dal rice", "tag": "Comfort Meal", "desc": "Simple and satisfying lentil curry with steamed rice"},
            {"dish": "rajma chawal", "tag": "North Indian", "desc": "Kidney bean curry served with basmati rice"}
        ])
    
    # Based on craving
    if craving.lower() == "sweet":
        contextual_dishes.extend([
            {"dish": "classic gulab jamun", "tag": "Indian Dessert", "desc": "Soft milk dumplings in rose-flavored sugar syrup"},
            {"dish": "chocolate barfi", "tag": "Fusion Sweet", "desc": "Rich chocolate fudge with traditional Indian touch"}
        ])
    
    # Based on vegetarian preference
    if veg.lower() == "true":
        contextual_dishes.extend([
            {"dish": "paneer tikka", "tag": "Vegetarian Grilled", "desc": "Marinated cottage cheese cubes grilled to perfection"},
            {"dish": "chole bhature", "tag": "North Indian", "desc": "Spicy chickpea curry with fluffy fried bread"}
        ])
    else:
        contextual_dishes.extend([
            {"dish": "butter chicken", "tag": "Popular Non-Veg", "desc": "Creamy tomato-based chicken curry"},
            {"dish": "fish curry", "tag": "Coastal Special", "desc": "Fresh fish cooked in aromatic spices and coconut"}
        ])
    
    # Return 6 unique dishes
    unique_dishes = []
    seen_names = set()
    for dish in contextual_dishes:
        if dish["dish"] not in seen_names and len(unique_dishes) < 6:
            unique_dishes.append(dish)
            seen_names.add(dish["dish"])
    
    # Fill remaining slots with general fallback if needed
    while len(unique_dishes) < 6:
        for fallback in FALLBACK_DISHES:
            if fallback["dish"] not in seen_names and len(unique_dishes) < 6:
                unique_dishes.append(fallback)
                seen_names.add(fallback["dish"])
    
    return unique_dishes[:6]

# Validate arguments
args = sys.argv[1:]
if len(args) != 10:
    print(json.dumps({"error": "Expected 10 arguments"}))
    sys.exit(1)

location, mood, veg, hunger, cuisine, craving, city, local_time, temp_c, condition = args
veg_text = "vegetarian" if veg.lower() == "true" else "non-vegetarian"

# Enhanced prompt with better structure and examples
prompt = f"""Based on the following context, suggest exactly 6 authentic Indian food or drink items:

CONTEXT:
- Location: {location}, {city}
- Current mood: {mood}
- Weather: {condition}, {temp_c}°C
- Local time: {local_time}
- Diet: {veg_text}
- Hunger level: {hunger}
- Craving: {craving}
- Preferred cuisine: {cuisine}

IMPORTANT RULES:
1. Use ONLY authentic Indian dish names as they appear on food delivery apps
2. For items with variations, always specify the type (e.g., "paneer samosa", "chicken biriyani", "vanilla ice cream")
3. Never use generic names like "samosa", "biriyani", "ice cream" without specifiers
4. Use "biriyani" not "biryani"
5. Match suggestions to the weather, time, and mood
6. Prioritize {craving} items if specified

EXAMPLES OF GOOD DISH NAMES:
- "classic masala chai" (not just "chai")
- "chicken biriyani" (not just "biriyani")  
- "paneer butter masala" (not just "paneer")
- "vanilla ice cream" (not just "ice cream")
- "classic vada pav" (not just "vada pav")

Return ONLY a JSON array with this exact structure:
[
  {{"dish": "specific dish name", "tag": "descriptive category", "desc": "appealing description"}},
  {{"dish": "specific dish name", "tag": "descriptive category", "desc": "appealing description"}},
  {{"dish": "specific dish name", "tag": "descriptive category", "desc": "appealing description"}},
  {{"dish": "specific dish name", "tag": "descriptive category", "desc": "appealing description"}},
  {{"dish": "specific dish name", "tag": "descriptive category", "desc": "appealing description"}},
  {{"dish": "specific dish name", "tag": "descriptive category", "desc": "appealing description"}}
]

Make each description 8-15 words explaining why this dish suits the current context."""

# Try multiple attempts to get good suggestions
max_attempts = 3
parsed = None

for attempt in range(max_attempts):
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Indian food curator. Return ONLY valid JSON with 6 authentic Indian dishes. Never use placeholder values or generic names. Always specify dish variations clearly."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2 + (attempt * 0.1),  # Slightly increase temperature each attempt
            max_tokens=800
        )
        
        raw_output = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        match = re.search(r'\[\s*{.*?}\s*\]', raw_output, re.DOTALL)
        json_str = match.group() if match else raw_output
        
        # Parse JSON
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError:
            try:
                parsed = ast.literal_eval(json_str)
            except Exception:
                continue
        
        # Validate the output
        if (isinstance(parsed, list) and 
            len(parsed) == 6 and 
            all(isinstance(item, dict) and 
                all(key in item for key in ["dish", "tag", "desc"]) 
                for item in parsed) and
            validate_dish_quality(parsed)):
            break
        else:
            parsed = None
            
    except Exception as e:
        continue

# Use contextual fallback if all attempts failed
if not parsed:
    parsed = get_contextual_fallback(mood, temp_c, hunger, craving, veg)

# Clean and standardize the output
final_output = []
for item in parsed:
    clean_item = {
        "dish": str(item.get("dish", "")).strip().lower(),
        "tag": str(item.get("tag", "")).strip().title(),
        "desc": str(item.get("desc", "")).strip().replace(""", '"').replace(""", '"')
    }
    
    # Ensure no empty values
    if not clean_item["dish"]:
        clean_item["dish"] = "classic masala chai"
    if not clean_item["tag"]:
        clean_item["tag"] = "Popular Choice"
    if not clean_item["desc"]:
        clean_item["desc"] = "A delicious option perfect for your current mood and preference"
    
    final_output.append(clean_item)

# Final validation - if we still have issues, use guaranteed fallback
if not validate_dish_quality(final_output):
    final_output = get_contextual_fallback(mood, temp_c, hunger, craving, veg)

# Output clean JSON
print(json.dumps(final_output, ensure_ascii=False))


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

# # Default fallback template (model only fills values)
# DEFAULT_TEMPLATE = [
#     {"dish": "Dish 1", "tag": "Tag 1", "desc": "Description 1"},
#     {"dish": "Dish 2", "tag": "Tag 2", "desc": "Description 2"},
#     {"dish": "Dish 3", "tag": "Tag 3", "desc": "Description 3"},
#     {"dish": "Dish 4", "tag": "Tag 4", "desc": "Description 4"},
#     {"dish": "Dish 5", "tag": "Tag 5", "desc": "Description 5"},
#     {"dish": "Dish 6", "tag": "Tag 6", "desc": "Description 6"}
# ]

# # Validate arguments
# args = sys.argv[1:]
# if len(args) != 10:
#     print(json.dumps({"error": "Expected 10 arguments"}))
#     sys.exit(1)

# location, mood, veg, hunger, cuisine, craving, city, local_time, temp_c, condition = args
# veg_text = "vegetarian" if veg.lower() == "true" else "non-vegetarian"

# # Construct prompt
# prompt = (
#     f"I'm feeling {mood} right now. The weather is {condition.lower()} and it's {temp_c}°C in {city}. "
#     f"The local time is {local_time}, and I'm currently in {location}. "
#     f"My diet preference is {veg_text}, my hunger level is {hunger}, and I'm craving something {craving}. "
#     +
#     ("Please ignore my usual cuisine preferences and suggest cold or refreshing *Indian-style* items like classic cold coffee, buttermilk, or fruit juice. "
#      if craving.lower() == "cold"
#      else f"I usually enjoy {cuisine} cuisine. ") +
#     ("Only suggest snack items like chips, samosas, or street-style chaats that are suitable for my situation. Don't suggest rice dishes or beverages. "
#      if hunger.lower() == "snack" else "") +
#     ("Only suggest popular Indian dessert items like gulab jamun, rasmalai, or payasam that satisfy my sweet craving. "
#      if craving.lower() == "sweet" else "") +
#     "Considering all this, suggest the top 6 food or drink options that would best suit my mood, weather, time, and preferences. "
#     "Make sure the suggestions use simple, popular, and widely available dish names — avoid fancy or Western items like sorbet or kombucha. "
#     "Use names exactly as they might appear in Indian food delivery apps like Swiggy — for example, prefer 'classic cold coffee' over 'cold coffee', and 'plain chai' instead of 'chai'. "
#     "For any item with variations (like vada pav, samosa, dosa, biriyani, gulab jamun, lassi, ice cream, falooda), clearly mention the specific flavor or style — for example, say 'classic vada pav', 'paneer samosa', 'chocolate ice cream', or 'classic gulab jamun'. "
#     "Do not use vague or generic dish names like 'ice cream', 'chai', or 'samosa' without a modifier. "
#     "Fill the following array with your suggestions. Keep the structure exactly the same and only replace the values:\n" +
#     json.dumps(DEFAULT_TEMPLATE, ensure_ascii=False) +
#     "\nReturn only the valid JSON array exactly in the same structure."
#     "Replace all values in this array with appropriate dishes. Return the same array, structure unchanged."
#     "Replace every placeholder value in the array below with real Indian dishes, tags, and descriptions. Do NOT return any value like 'dish': Dish 1', 'tag': 'Tag 1'"
#     "Its 'biriyani', not 'biryani'."
# )

# # Send request to Groq API
# response = client.chat.completions.create(
#     model="llama3-70b-8192",
#     messages=[
#         {
#             "role": "system",
#             "content": "You are a helpful food recommendation assistant. Return ONLY a valid JSON array of 6 Indian food/drink items based on user context. Do not add any extra text."
#         },
#         {"role": "user", "content": prompt}
#     ],
#     temperature=0.3,
#     max_tokens=600
# )

# raw_output = response.choices[0].message.content.strip()

# # Try extracting JSON from response
# match = re.search(r'\[\s*{.*?}\s*]', raw_output, re.DOTALL)
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

# # Use fallback template if parsing fails
# if not isinstance(parsed, list) or len(parsed) != 6:
#     parsed = DEFAULT_TEMPLATE

# # Clean and standardize the output
# final_output = []
# for item in parsed:
#     clean_item = {
#         "dish": str(item.get("dish", "")).strip(),
#         "tag": str(item.get("tag", "")).strip(),
#         "desc": str(item.get("desc", "")).strip().replace("”", '"').replace("“", '"')
#     }
#     final_output.append(clean_item)

# # Output clean JSON
# print(json.dumps(final_output, ensure_ascii=False))

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

# # Validate arguments
# args = sys.argv[1:]
# if len(args) != 10:
#     print(json.dumps({ "error": "Expected 10 arguments" }))
#     sys.exit(1)

# location, mood, veg, hunger, cuisine, craving, city, local_time, temp_c, condition = args
# veg_text = "vegetarian" if veg.lower() == "true" else "non-vegetarian"

# # Construct prompt
# prompt = (
#     f"I'm feeling {mood} right now. The weather is {condition.lower()} and it's {temp_c}°C in {city}. "
#     f"The local time is {local_time}, and I'm currently in {location}. "
#     f"My diet preference is {veg_text}, my hunger level is {hunger}, and I'm craving something {craving}. "
#     +
#     ("Please ignore my usual cuisine preferences and suggest cold or refreshing *Indian-style* items like classic cold coffee, buttermilk, or fruit juice. "
#      if craving.lower() == "cold"
#      else f"I usually enjoy {cuisine} cuisine. ") +
#     ("Only suggest snack items like chips, samosas, or street-style chaats that are suitable for my situation. Don't suggest rice dishes or beverages. "
#      if hunger.lower() == "snack" else "") +
#     ("Only suggest popular Indian dessert items like gulab jamun, rasmalai, or payasam that satisfy my sweet craving. "
#      if craving.lower() == "sweet" else "") +
#     "Considering all this, suggest the top 6 food or drink options that would best suit my mood, weather, time, and preferences. "
#     "Make sure the suggestions use simple, popular, and widely available dish names — avoid fancy or Western items like sorbet or kombucha. "
#     "Use names exactly as they might appear in Indian food delivery apps like Swiggy — for example, prefer 'classic cold coffee' over 'iced latte', and 'plain chai' instead of 'spiced infusion'. "
#     "For any item with variations (like vada pav, samosa, dosa, biryani, gulab jamun, lassi, ice cream), clearly mention the specific flavor or style — for example, say 'classic vada pav', 'paneer samosa', 'chocolate ice cream', or 'classic gulab jamun'. "
#     "Do not use vague or generic dish names like 'ice cream', 'chai', or 'samosa' without a modifier. "
#     "For each option, return a JSON object with keys 'dish', 'tag', and 'desc'. Use only valid JSON with double quotes for all keys and values. "
#     "Do not include any markdown, explanation, or extra text. Output only the array like: "
#     "[{\"dish\": \"...\", \"tag\": \"...\", \"desc\": \"...\"}, ...]"
#     "Return only valid JSON array without extra characters or explanation."
# )

# # Send request
# response = client.chat.completions.create(
#     model="llama3-70b-8192",
#     messages=[
#         {"role": "system", "content": "You are a helpful food recommendation assistant. Return ONLY a valid JSON array of 6 Indian food/drink items based on user context."},
#         {"role": "user", "content": prompt}
#     ],
#     temperature=0.3,
#     max_tokens=600
# )

# # Output from model
# raw_output = response.choices[0].message.content.strip()

# # Try to find the array using strict regex
# match = re.search(r'\[\s*{.*?}\s*]', raw_output, re.DOTALL)
# json_str = match.group() if match else raw_output  # fallback to full response

# # Try loading via json or ast
# def parse_json(data):
#     try:
#         return json.loads(data)
#     except json.JSONDecodeError:
#         try:
#             return ast.literal_eval(data)
#         except Exception:
#             return None

# parsed = parse_json(json_str)

# # Validate result
# if isinstance(parsed, list) and all(isinstance(x, dict) for x in parsed):
#     print(json.dumps(parsed))
# else:
#     print(json.dumps({ "error": "Invalid JSON format", "raw": raw_output }))


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

# # Validate arguments
# args = sys.argv[1:]
# if len(args) != 10:
#     print(json.dumps({"error": "Expected 10 arguments"}))
#     sys.exit(1)

# location, mood, veg, hunger, cuisine, craving, city, local_time, temp_c, condition = args
# veg_text = "vegetarian" if veg.lower() == "true" else "non-vegetarian"

# # Construct prompt
# prompt = (
#     f"I'm feeling {mood} right now. The weather is {condition.lower()} and it's {temp_c}°C in {city}. "
#     f"The local time is {local_time}, and I'm currently in {location}. "
#     f"My diet preference is {veg_text}, my hunger level is {hunger}, and I'm craving something {craving}. "
#     +
#     ("Please ignore my usual cuisine preferences and suggest cold or refreshing *Indian-style* items like classic cold coffee, buttermilk, or fruit juice. "
#      if craving.lower() == "cold"
#      else f"I usually enjoy {cuisine} cuisine. ") +
#     ("Only suggest snack items like chips, samosas, or street-style chaats that are suitable for my situation. Don't suggest rice dishes or beverages. "
#      if hunger.lower() == "snack" else "") +
#     ("Only suggest popular Indian dessert items like gulab jamun, rasmalai, or payasam that satisfy my sweet craving. "
#      if craving.lower() == "sweet" else "") +
#     "Considering all this, suggest the top 6 food or drink options that would best suit my mood, weather, time, and preferences. "
#     "Make sure the suggestions use simple, popular, and widely available dish names — avoid fancy or Western items like sorbet or kombucha. "
#     "Use names exactly as they might appear in Indian food delivery apps like Swiggy — for example, prefer 'classic cold coffee' over 'iced latte', and 'plain chai' instead of 'spiced infusion'. "
#     "For any item with variations (like vada pav, samosa, dosa, biryani, gulab jamun, lassi, ice cream, falooda), clearly mention the specific flavor or style — for example, say 'classic vada pav', 'paneer samosa', 'chocolate ice cream', or 'classic gulab jamun'. "
#     "Do not use vague or generic dish names like 'ice cream', 'chai', or 'samosa' without a modifier. "
#     "For each option, return a JSON object with keys 'dish', 'tag', and 'desc'. Use only valid JSON with double quotes for all keys and values. "
#     "Do not include any markdown, explanation, or extra text. Output only the array like: "
#     "[{\"dish\": \"...\", \"tag\": \"...\", \"desc\": \"...\"}, ...]"
#     "Return only valid JSON array without extra characters or explanation."
# )

# # Send request
# response = client.chat.completions.create(
#     model="llama3-70b-8192",
#     messages=[
#         {"role": "system", "content": "You are a helpful food recommendation assistant. Return ONLY a valid JSON array of 6 Indian food/drink items based on user context."},
#         {"role": "user", "content": prompt}
#     ],
#     temperature=0.3,
#     max_tokens=600
# )

# raw_output = response.choices[0].message.content.strip()

# # Attempt to find valid JSON array
# match = re.search(r'\[\s*{.*?}\s*]', raw_output, re.DOTALL)
# json_str = match.group() if match else raw_output

# # Fallback parser
# def parse_json(data):
#     try:
#         return json.loads(data)
#     except json.JSONDecodeError:
#         try:
#             return ast.literal_eval(data)
#         except Exception:
#             return None

# parsed = parse_json(json_str)

# # Rebuild into clean standard JSON
# final_output = []

# if isinstance(parsed, list):
#     for item in parsed:
#         if isinstance(item, dict):
#             clean_item = {
#                 "dish": str(item.get("dish", "")).strip(),
#                 "tag": str(item.get("tag", "")).strip(),
#                 "desc": str(item.get("desc", "")).strip().replace("”", '"').replace("“", '"')
#             }
#             if clean_item["dish"] and clean_item["tag"] and clean_item["desc"]:
#                 final_output.append(clean_item)

# # Output
# if len(final_output) == 6:
#     print(json.dumps(final_output, ensure_ascii=False))
# else:
#     print(json.dumps({
#         "error": "Invalid JSON format or incomplete items",
#         "raw": raw_output
#     }))