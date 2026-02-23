import json
import re

def load_data():
    """Load placement data from JSON file."""
    try:
        with open("data/placements.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def process_query(query):
    """Process user query and return matching companies with robust parsing."""
    query = query.lower().strip()
    data = load_data()
    if not data:
        return "⚠️ Data source not found."

    year = cgpa = company = role = domain = tech_filter = month = None
    ask_package = ask_hiring = False

    # 1. Detect Year (Regex)
    year_match = re.search(r'\b(202[345])\b', query)
    if year_match:
        year = int(year_match.group(1))

    # 2. Detect CGPA (Regex for float/int + operator)
    cgpa_match = re.search(r'(?:cgpa\s*)?(\d+(?:\.\d+)?)(\+)?', query)
    cgpa_operator = "criteria" # NEW DEFAULT: Treat "8 CGPA" as "Companies requiring 8"
    if cgpa_match:
        val = float(cgpa_match.group(1))
        has_plus = cgpa_match.group(2) == "+"
        if 5 <= val <= 10:
            cgpa = val
            # Detect Eligibility Search (If user is talking about their own score)
            if any(kw in query for kw in ["eligible", "i have", "my", "for", "at", "can i"]):
                cgpa_operator = "eligible"
            # Explicitly force criteria if operator or keywords like 'above' exist
            elif has_plus or any(kw in query for kw in ["above", "higher", "minimum", "min", "at least", ">", "requiring", "needs"]):
                cgpa_operator = "criteria"

    # 3. Detect Company (Check list)
    for item in data:
        comp_name = item["company"].lower()
        if comp_name in query:
            company = item["company"]
            break

    # 4. Detect Domain
    domains = [
        'fintech', 'edtech', 'saas', 'healthtech', 'ecommerce', 'logistics',
        'mobility', 'media', 'realestate', 'it services', 'insurtech'
    ]
    for d in domains:
        if d in query:
            domain = d
            break

    # 5. Detect Role
    roles_all = [
        'sde', 'frontend', 'backend', 'full stack', 'product manager',
        'qa engineer', 'ml engineer', 'data engineer', 'support engineer', 'analyst'
    ]
    for r in roles_all:
        if r in query:
            role = r
            break

    # 6. Detect Month
    months_map = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12"
    }
    for m, code in months_map.items():
        if m in query:
            month = code
            break

    # 7. Tech/Non-Tech Filter
    if re.search(r'non[- ]?tech', query):
        tech_filter = "non-tech"
    elif "tech" in query:
        tech_filter = "tech"

    # 8. Intent Detection (Expanded Synonyms)
    ask_package = any(kw in query for kw in ["package", "salary", "lpa", "pay", "ctc", "stipend", "money", "much", "worth"])
    ask_hiring = any(kw in query for kw in ["hiring", "interview", "selection", "process", "rounds", "test", "eligible", "procedure"])
    ask_date = any(kw in query for kw in ["date", "when", "visit", "visiting", "arrival", "schedule", "time"])
    ask_role = any(kw in query for kw in ["role", "position", "job", "profile", "designation", "work"])
    
    # Aggregate triggers
    is_highest = any(kw in query for kw in ["highest", "max", "best", "top", "greatest"])
    is_lowest = any(kw in query for kw in ["lowest", "min", "least", "bottom", "cheapest"])
    is_count = any(kw in query for kw in ["how many", "count", "number of", "total", "list"])

    # --- Filtering Logic ---
    results = []
    # Check for "show all" intent
    show_all = any(kw in query for kw in ["show all", "all companies", "list all"])
    
    for item in data:
        if show_all:
            results.append(item)
            continue

        if year and item.get("year") != year:
            continue
        
        # Smart CGPA Filtering
        if cgpa:
            min_req = item.get("min_cgpa", 0)
            if cgpa_operator == "criteria":
                if min_req < cgpa: continue # "8+" shows only 8, 8.5, 9
            else:
                if min_req > cgpa: continue # "I have 7" shows only <= 7

        if company and item.get("company", "").lower() != company.lower():
            continue
        if domain and domain.lower() not in item.get("domain", "").lower():
            continue
        if role and role not in str(item.get("roles_offered", "")).lower():
            continue
        if tech_filter and item.get("company_type", "").lower() != tech_filter:
            continue
        if month and item.get("visit_date", "").split("-")[1] != month:
            continue
        results.append(item)

    # --- Keyword Echoing Construction ---
    detected_tags = []
    if show_all: detected_tags.append("🌐 <b>ALL COMPANIES</b>")
    if company: detected_tags.append(f"🏢 <b>{company}</b>")
    if year: detected_tags.append(f"📅 <b>{year}</b>")
    
    if cgpa:
        label = f"{cgpa}+ REQ" if cgpa_operator == "criteria" else f"FOR {cgpa} CGPA"
        detected_tags.append(f"🎓 <b>{label}</b>")
        
    if role: detected_tags.append(f"👔 <b>{role.upper()}</b>")
    if tech_filter: detected_tags.append(f"⚙️ <b>{tech_filter.upper()}</b>")
    if month: detected_tags.append(f"🗓️ <b>MONTH-{month}</b>")
    
    tag_html = ""
    if detected_tags:
        tag_html = f"<div style='display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;opacity:0.8;font-size:0.85rem'>FOUND: {' '.join(detected_tags)}</div>"

    if not results:
        return (
            tag_html + "😕 No matching companies found. Try something like: "
            "<i>'Highest package in 2025'</i> or <i>'When is Amazon visiting?'</i>"
        )

    # --- Precise Query Handling ---
    
    # 1. Handle Aggregates
    if is_highest:
        match = max(results, key=lambda x: x.get("package_lpa", 0))
        return tag_html + f"🚀 The <b>highest package</b> found is <b>₹{match['package_lpa']} LPA</b> offered by <b>{match['company']}</b>."
    
    if is_lowest:
        match = min(results, key=lambda x: x.get("package_lpa", 999))
        return tag_html + f"📉 The <b>lowest package</b> among these is <b>₹{match['package_lpa']} LPA</b> offered by <b>{match['company']}</b>."
    
    if is_count:
        context = f"in {year}" if year else ""
        return tag_html + f"📊 I found <b>{len(results)} companies</b> matching your request {context}."

    # 2. Handle Specific Company Questions
    if company:
        match = results[0]
        if ask_package:
            return tag_html + f"💰 <b>{match['company']}</b> offers a package of <b>₹{match['package_lpa']} LPA</b>."
        if ask_hiring:
            return tag_html + f"🧩 <b>Hiring process of {match['company']}</b>: {match['hiring_process']}"
        if ask_date:
            return tag_html + f"📅 <b>{match['company']}</b> is scheduled to visit on <b>{match['visit_date']}</b>."
        if ask_role:
            return tag_html + f"👔 <b>{match['company']}</b> is offering roles like: <b>{match.get('roles_offered', 'General Roles')}</b>."

    # 3. Handle Field-Specific General Questions (e.g., "dates of tech companies")
    if ask_date and len(results) <= 5:
        dates = [f"• <b>{r['company']}</b>: {r['visit_date']}" for r in results]
        return tag_html + "📅 Here are the visit dates:<br/>" + "<br/>".join(dates)

    # 4. Default: Dynamic Summary + Table
    summary = "📋 I found these companies"
    if year: summary += f" for <b>{year}</b>"
    if cgpa: summary += f" for <b>{cgpa}+ CGPA</b>"
    if tech_filter: summary += f" in <b>{tech_filter}</b> category"
    
    reply = tag_html + f"<p style='margin-bottom:8px'>{summary}:</p>"
    reply += '<div class="table-wrapper"><table><thead><tr>'
    reply += '<th>Company</th><th>Role</th><th>Package</th><th>Min CGPA</th><th>Visit Date</th>'
    reply += '</tr></thead><tbody>'

    # Limit table to 15 rows for better mobile experience, then add "..."
    for comp in results[:15]:
        reply += f'<tr><td>{comp["company"]}</td><td>{comp.get("roles_offered", "—")}</td>'
        reply += f'<td>₹{comp["package_lpa"]} LPA</td><td>{comp["min_cgpa"]}</td>'
        reply += f'<td>{comp["visit_date"]}</td></tr>'
        
    if len(results) > 15:
        reply += f"<tr><td colspan='5' style='text-align:center'><i>... and {len(results)-15} more</i></td></tr>"
        
    reply += "</tbody></table></div>"

    return reply.strip()
