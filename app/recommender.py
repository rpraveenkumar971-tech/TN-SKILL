import json
import re
import urllib.parse
from typing import Optional

from .config import (
    GOOGLE_API_KEY,
    GEMINI_MODEL
)


# ---------------------------------------------------------
# Gemini import
# ---------------------------------------------------------

try:

    from google import genai
    from google.genai import types

except Exception:

    genai = None
    types = None


# =========================================================
# JSON extraction
# =========================================================

def extract_json(text: str) -> dict:

    if not text:
        raise ValueError(
            "Empty AI response"
        )

    text = text.strip()

    # Remove markdown code fences
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
        flags=re.IGNORECASE
    )

    try:

        return json.loads(text)

    except json.JSONDecodeError:

        # Try to find JSON object
        match = re.search(
            r"\{.*\}",
            text,
            re.DOTALL
        )

        if not match:

            raise ValueError(
                "AI did not return valid JSON"
            )

        return json.loads(
            match.group(0)
        )


# =========================================================
# Shopping URLs
# =========================================================

def shopping_links(
    term: str,
    platforms
):

    term = term or "product"

    query = urllib.parse.quote_plus(
        term
    )

    urls = {

        "amazon":
            f"https://www.amazon.in/s?k={query}",

        "flipkart":
            f"https://www.flipkart.com/search?q={query}",

        "myntra":
            f"https://www.myntra.com/{query}",

        "meesho":
            f"https://www.meesho.com/search?q={query}",

        "google":
            f"https://www.google.com/search?q={query}",

        "swiggy":
            f"https://www.swiggy.com/search?query={query}",

        "zomato":
            f"https://www.zomato.com/search?q={query}",

        "bigbasket":
            f"https://www.bigbasket.com/ps/?q={query}",

        "bookmyshow":
            f"https://in.bookmyshow.com/explore/search?q={query}",

        "booking":
            f"https://www.booking.com/search.html?ss={query}",

        "makemytrip":
            "https://www.makemytrip.com/hotels/"
            f"hotel-listing/?searchText={query}",

        "oyorooms":
            "https://www.oyorooms.com/search/"
            f"?location={query}",

        "nobroker":
            "https://www.nobroker.in/property/search"
            f"?searchTerm={query}",

        "bluestone":
            "https://www.bluestone.com/search.html"
            f"?query={query}",

        "tanishq":
            f"https://www.tanishq.co.in/search?q={query}",

        "caratlane":
            f"https://www.caratlane.com/search?q={query}",

        "melorra":
            f"https://www.melorra.com/search?q={query}"
    }

    return {
        platform: urls[platform]
        for platform in platforms
        if platform in urls
    }


# =========================================================
# Gemini API
# =========================================================

def call_gemini(
    prompt: str
) -> Optional[dict]:

    if not GOOGLE_API_KEY:

        return None

    if genai is None:

        return None

    try:

        client = genai.Client(
            api_key=GOOGLE_API_KEY
        )

        response = client.models.generate_content(

            model=GEMINI_MODEL,

            contents=prompt,

            config=types.GenerateContentConfig(

                response_mime_type="application/json",

                temperature=0.4
            )
        )

        return extract_json(
            response.text
        )

    except Exception as error:

        print(
            "Gemini API error:",
            error
        )

        return None


# =========================================================
# Normalize budget
# =========================================================

def normalize_budget(
    result: dict,
    budget: float
):

    result["total_budget"] = float(
        budget
    )

    breakdown = result.get(
        "budget_breakdown",
        []
    )

    total = 0.0

    for category in breakdown:

        for item in category.get(
            "items",
            []
        ):

            price = float(
                item.get(
                    "estimated_price",
                    0
                )
            )

            quantity = max(
                1,
                int(
                    item.get(
                        "quantity",
                        1
                    )
                )
            )

            total += price * quantity

    # If AI accidentally exceeds budget,
    # scale item prices proportionally.
    if total > budget and total > 0:

        factor = budget / total

        for category in breakdown:

            for item in category.get(
                "items",
                []
            ):

                item["estimated_price"] = round(
                    float(
                        item.get(
                            "estimated_price",
                            0
                        )
                    ) * factor,
                    2
                )

    final_total = 0.0

    for category in breakdown:

        allocation = 0.0

        for item in category.get(
            "items",
            []
        ):

            item["quantity"] = max(
                1,
                int(
                    item.get(
                        "quantity",
                        1
                    )
                )
            )

            item["estimated_price"] = round(
                float(
                    item.get(
                        "estimated_price",
                        0
                    )
                ),
                2
            )

            allocation += (
                item["estimated_price"]
                * item["quantity"]
            )

            search_term = (
                item.get("search_terms")
                or item.get("name")
                or "product"
            )

            item["shopping_links"] = shopping_links(
                search_term,
                [
                    "amazon",
                    "flipkart",
                    "google"
                ]
            )

        category["allocation"] = round(
            allocation,
            2
        )

        final_total += allocation

    result["spent_amount"] = round(
        final_total,
        2
    )

    result["remaining_budget"] = round(
        max(0, budget - final_total),
        2
    )

    return result


# =========================================================
# HOME INTERIOR
# =========================================================

def home(inp):

    prompt = f"""
You are PocketSmart AI, a budget planning assistant.

Create an India-specific home interior
budget plan.

Currency: INR

Total budget:
₹{inp.total_budget}

Requirements:

Lights:
{inp.num_lights}

Fans:
{inp.num_fans}

Furniture pieces:
{inp.num_furniture}

Dining tables:
{inp.num_dining_tables}

Living room:
{inp.has_living_room}

Kitchen:
{inp.has_kitchen}

Bedroom:
{inp.has_bedroom}

Additional requirements:
{inp.additional_requirements}

Important:

1. Keep the complete plan within the budget.
2. Use realistic Indian-market estimates.
3. Give useful product search terms.
4. Prioritize essential items.
5. Do not invent exact live product prices.
6. Return ONLY valid JSON.

JSON format:

{{
    "total_budget": 0,
    "budget_breakdown": [
        {{
            "category": "Lighting",
            "allocation": 0,
            "items": [
                {{
                    "name": "",
                    "description": "",
                    "estimated_price": 0,
                    "quantity": 1,
                    "search_terms": ""
                }}
            ]
        }}
    ],
    "additional_suggestions": []
}}
"""

    result = call_gemini(
        prompt
    )

    if not result:

        result = local_home(
            inp
        )

    return normalize_budget(
        result,
        inp.total_budget
    )


def local_home(i):

    lights = max(
        i.num_lights,
        1
    )

    fans = max(
        i.num_fans,
        1
    )

    furniture = max(
        i.num_furniture,
        1
    )

    return {

        "total_budget":
            i.total_budget,

        "budget_breakdown": [

            {
                "category":
                    "Lighting",

                "allocation":
                    i.total_budget * 0.20,

                "items": [

                    {
                        "name":
                            "LED Lighting",

                        "description":
                            "Energy-efficient LED lighting.",

                        "estimated_price":
                            max(
                                150,
                                (
                                    i.total_budget
                                    * 0.20
                                    / lights
                                )
                            ),

                        "quantity":
                            lights,

                        "search_terms":
                            "LED lights home India"
                    }
                ]
            },

            {
                "category":
                    "Fans",

                "allocation":
                    i.total_budget * 0.25,

                "items": [

                    {
                        "name":
                            "Ceiling Fan",

                        "description":
                            "Energy-efficient ceiling fan.",

                        "estimated_price":
                            max(
                                1800,
                                (
                                    i.total_budget
                                    * 0.25
                                    / fans
                                )
                            ),

                        "quantity":
                            fans,

                        "search_terms":
                            "ceiling fan India"
                    }
                ]
            },

            {
                "category":
                    "Furniture",

                "allocation":
                    i.total_budget * 0.25,

                "items": [

                    {
                        "name":
                            "Home Furniture",

                        "description":
                            "Practical furniture for selected rooms.",

                        "estimated_price":
                            max(
                                3000,
                                (
                                    i.total_budget
                                    * 0.25
                                    / furniture
                                )
                            ),

                        "quantity":
                            furniture,

                        "search_terms":
                            "home furniture India"
                    }
                ]
            }
        ],

        "additional_suggestions": [

            "Compare multiple Indian marketplaces.",

            "Prioritize essential furniture first.",

            "Keep part of the budget as contingency."
        ]
    }


# =========================================================
# PARTY PLANNER
# =========================================================

def party(i):

    prompt = f"""
Create an India-specific party budget plan.

Budget:
₹{i.total_budget}

Party type:
{i.party_type}

Number of guests:
{i.num_guests}

Venue:
{i.venue_type}

Catering:
{i.needs_catering}

Decoration:
{i.needs_decoration}

Entertainment:
{i.needs_entertainment}

Additional requirements:
{i.additional_requirements}

Requirements:

- Use INR.
- Keep the total within the budget.
- Provide practical categories.
- Include venue suggestions.
- Include search terms.
- Do not claim live prices.
- Return ONLY JSON.

Required JSON:

{{
    "total_budget": 0,
    "budget_breakdown": [],
    "venue_suggestions": [],
    "additional_suggestions": []
}}
"""

    result = call_gemini(
        prompt
    )

    if not result:

        result = local_party(
            i
        )

    result = normalize_budget(
        result,
        i.total_budget
    )

    for venue in result.get(
        "venue_suggestions",
        []
    ):

        search_term = (
            venue.get("search_terms")
            or venue.get("name")
            or "party venue"
        )

        venue["search_links"] = shopping_links(
            search_term,
            [
                "google",
                "booking",
                "makemytrip",
                "oyorooms",
                "nobroker"
            ]
        )

    return result


def local_party(i):

    categories = []

    # Venue
    categories.append({

        "category":
            "Venue",

        "allocation":
            i.total_budget * 0.25,

        "items": [

            {
                "name":
                    i.venue_type
                    or "Event Venue",

                "description":
                    "Venue allowance.",

                "estimated_price":
                    i.total_budget * 0.25,

                "quantity":
                    1,

                "search_terms":
                    (
                        i.venue_type
                        or "party venue"
                    )
            }
        ]
    })

    # Catering
    if i.needs_catering:

        categories.append({

            "category":
                "Catering",

            "allocation":
                i.total_budget * 0.40,

            "items": [

                {
                    "name":
                        "Catering Package",

                    "description":
                        (
                            f"Food service for "
                            f"{i.num_guests} guests."
                        ),

                    "estimated_price":
                        i.total_budget * 0.40,

                    "quantity":
                        1,

                    "search_terms":
                        "party catering"
                }
            ]
        })

    # Decoration
    if i.needs_decoration:

        categories.append({

            "category":
                "Decoration",

            "allocation":
                i.total_budget * 0.15,

            "items": [

                {
                    "name":
                        "Party Decoration",

                    "description":
                        "Theme and table decoration.",

                    "estimated_price":
                        i.total_budget * 0.15,

                    "quantity":
                        1,

                    "search_terms":
                        "party decoration"
                }
            ]
        })

    # Entertainment
    if i.needs_entertainment:

        categories.append({

            "category":
                "Entertainment",

            "allocation":
                i.total_budget * 0.10,

            "items": [

                {
                    "name":
                        "Entertainment",

                    "description":
                        "Music, games and activities.",

                    "estimated_price":
                        i.total_budget * 0.10,

                    "quantity":
                        1,

                    "search_terms":
                        "party entertainment"
                }
            ]
        })

    return {

        "total_budget":
            i.total_budget,

        "budget_breakdown":
            categories,

        "venue_suggestions": [

            {
                "name":
                    i.venue_type
                    or "Local Party Venue",

                "type":
                    i.venue_type
                    or "Event Hall",

                "capacity":
                    i.num_guests,

                "estimated_cost":
                    i.total_budget * 0.25,

                "search_terms":
                    (
                        f"{i.venue_type or 'party venue'} "
                        f"{i.num_guests} guests"
                    )
            }
        ],

        "additional_suggestions": [

            "Get quotes from at least three vendors.",

            "Confirm cancellation policies before booking.",

            "Keep a small emergency budget."
        ]
    }


# =========================================================
# JEWELRY
# =========================================================

def jewelry(
    i,
    image_path=None
):

    if image_path:

        image_note = """
An outfit image has been uploaded.

The system should consider:
- outfit colors
- style
- formality
- suitable jewelry tone
- suitable jewelry style

Do not claim visual details that cannot actually
be determined from the image.
"""

    else:

        image_note = """
No outfit image was uploaded.
Use the occasion and preferences.
"""

    prompt = f"""
You are a jewelry recommendation assistant
for Indian users.

Budget:
₹{i.total_budget}

Occasion:
{i.occasion}

Preferences:
{i.preferences}

{image_note}

Provide practical recommendations.

Return ONLY JSON:

{{
    "outfit_analysis": {{
        "colors": [],
        "style": "",
        "formality": ""
    }},
    "total_budget": 0,
    "jewelry_recommendations": [
        {{
            "item_type": "",
            "description": "",
            "style": "",
            "estimated_price": 0,
            "search_terms": ""
        }}
    ],
    "additional_suggestions": []
}}

Keep estimated costs within budget.
Do not claim exact live product prices.
"""

    result = call_gemini(
        prompt
    )

    if not result:

        result = local_jewelry(
            i
        )

    result["total_budget"] = (
        i.total_budget
    )

    recommendations = result.get(
        "jewelry_recommendations",
        []
    )

    for item in recommendations:

        item["estimated_price"] = round(
            float(
                item.get(
                    "estimated_price",
                    0
                )
            ),
            2
        )

        search_term = (
            item.get("search_terms")
            or item.get("item_type")
            or "jewelry"
        )

        item["shopping_links"] = shopping_links(
            search_term,
            [
                "amazon",
                "flipkart",
                "bluestone",
                "tanishq",
                "caratlane",
                "melorra",
                "meesho"
            ]
        )

    # Keep jewelry recommendations within budget
    total = sum(
        float(
            item.get(
                "estimated_price",
                0
            )
        )
        for item in recommendations
    )

    if total > i.total_budget and total > 0:

        factor = (
            i.total_budget / total
        )

        for item in recommendations:

            item["estimated_price"] = round(
                float(
                    item["estimated_price"]
                ) * factor,
                2
            )

    spent = sum(
        float(
            item.get(
                "estimated_price",
                0
            )
        )
        for item in recommendations
    )

    result["spent_amount"] = round(
        spent,
        2
    )

    result["remaining_budget"] = round(
        max(
            0,
            i.total_budget - spent
        ),
        2
    )

    return result


def local_jewelry(i):

    budget = i.total_budget

    return {

        "outfit_analysis": {

            "colors":
                [],

            "style":
                "Not analyzed",

            "formality":
                i.occasion
        },

        "total_budget":
            budget,

        "jewelry_recommendations": [

            {
                "item_type":
                    "Earrings",

                "description":
                    "Versatile earrings suitable for the occasion.",

                "style":
                    "Contemporary",

                "estimated_price":
                    budget * 0.35,

                "search_terms":
                    "women earrings"
            },

            {
                "item_type":
                    "Necklace",

                "description":
                    "Statement necklace within the budget.",

                "style":
                    "Elegant",

                "estimated_price":
                    budget * 0.45,

                "search_terms":
                    "women necklace"
            },

            {
                "item_type":
                    "Bracelet",

                "description":
                    "Simple coordinating bracelet.",

                "style":
                    "Minimal",

                "estimated_price":
                    budget * 0.15,

                "search_terms":
                    "women bracelet"
            }
        ],

        "additional_suggestions": [

            "Match the metal tone with the outfit.",

            "Compare making charges and return policies.",

            "Keep some budget available for adjustments."
        ]
    }