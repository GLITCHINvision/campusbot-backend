"""
Module: chatbot.py
Description: Handles placement data queries for chatbot responses.
"""

import json


def load_data():
    """Load placement data from JSON file."""
    with open("data/placements.json", "r", encoding="utf-8") as file:
        return json.load(file)


def process_query(query):
    """Process user query and return matching companies."""
    query = query.lower()
    data = load_data()

    year = cgpa = company = role = domain = tech_filter = month = None
    ask_package = ask_hiring = False

    # Detect year
    for y in [2025, 2024, 2023]:
        if str(y) in query:
            year = y
            break

    # Detect CGPA
    words = query.split()
    for i, word in enumerate(words):
        if word == "cgpa" and i + 1 < len(words):
            try:
                cgpa = float(words[i + 1])
                break
            except ValueError:
                continue
        elif word.replace(".", "").isdigit():
            try:
                val = float(word)
                if 5 <= val <= 10:
                    cgpa = val
                    break
            except ValueError:
                continue

    # Detect company
    for item in data:
        if item["company"].lower() in query:
            company = item["company"]
            break

    # Detect domain
    domains = [
        'fintech', 'edtech', 'saas', 'healthtech', 'ecommerce', 'logistics',
        'mobility', 'media', 'realestate', 'it services', 'insurtech'
    ]
    for d in domains:
        if d in query:
            domain = d
            break

    # Detect role
    roles_all = [
        'sde', 'frontend', 'backend', 'full stack', 'product manager',
        'qa engineer', 'ml engineer', 'data engineer', 'support engineer', 'analyst'
    ]
    for r in roles_all:
        if r in query:
            role = r
            break

    # Detect month
    months = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12"
    }
    for m, code in months.items():
        if m in query:
            month = code
            break

    # Detect tech/non-tech filter
    if "non tech" in query or "non-tech" in query:
        tech_filter = "non-tech"
    elif "tech" in query:
        tech_filter = "tech"

    # Intent detection
    if "package" in query or "salary" in query:
        ask_package = True
    if any(
        kw in query for kw in [
            "hiring process", "interview process",
            "selection process", "recruitment process"
        ]
    ):
        ask_hiring = True

    # Filter matching results
    results = []
    for item in data:
        if year and item["year"] != year:
            continue
        if cgpa and item["min_cgpa"] > cgpa:
            continue
        if company and item["company"].lower() != company.lower():
            continue
        if domain and domain.lower() not in item.get("domain", "").lower():
            continue
        if role and role not in str(item.get("roles_offered", "")).lower():
            continue
        if tech_filter and item.get("company_type", "").lower() != tech_filter:
            continue
        if month and item["visit_date"].split("-")[1] != month:
            continue
        results.append(item)

    if not results:
        return (
            "😕 No matching companies found. Try modifying your query like: "
            "'tech roles in August with CGPA 8+'."
        )

    if ask_package and company:
        return (
            f"💰 <b>{company}</b> offers a package of "
            f"<b>₹{results[0]['package_lpa']} LPA</b>."
        )

    if ask_hiring and company:
        return (
            f"🧩 <b>Hiring process of {company}</b>: "
            f"{results[0]['hiring_process']}"
        )

    # Table output
    reply = f"<p>📋 Found <b>{len(results)}</b> company(ies):</p>"
    reply += """
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse;
           margin-top: 10px; font-size: 15px;">
        <tr style="background-color: #f0f0f0;">
            <th>Company</th>
            <th>Role</th>
            <th>Package</th>
            <th>Min CGPA</th>
            <th>Domain</th>
            <th>Visit Date</th>
        </tr>
    """
    for comp in results:
        reply += f"""
        <tr>
            <td>{comp['company']}</td>
            <td>{comp.get('roles_offered', '—')}</td>
            <td>₹{comp['package_lpa']} LPA</td>
            <td>{comp['min_cgpa']}</td>
            <td>{comp['domain']}</td>
            <td>{comp['visit_date']}</td>
        </tr>
        """
    reply += "</table>"

    return reply.strip()
