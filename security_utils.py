import re, secrets
from urllib.parse import urlparse

COMMON = {"password","password123","123456","12345678","qwerty","admin","admin123","welcome"}

def check_password_strength(password):
    score = 0; feedback=[]
    if len(password)>=14: score += 2
    elif len(password)>=10: score += 1
    else: feedback.append("Use at least 10 characters; 14+ is preferable.")
    for pattern, msg in [
        (r"[a-z]","Add lowercase letters."),
        (r"[A-Z]","Add uppercase letters."),
        (r"\d","Add numbers."),
        (r"[^A-Za-z0-9]","Add symbols.")
    ]:
        if re.search(pattern,password): score += 1
        else: feedback.append(msg)
    if password.lower() in COMMON:
        score=0; feedback.append("This is a commonly used password.")
    strength = "Weak" if score<=2 else "Moderate" if score<=4 else "Strong" if score==5 else "Very Strong"
    return {"strength":strength,"score":score,"feedback":feedback}

def analyze_url(url):
    result={"input":url,"risk_level":"Low","warnings":[],
            "note":"Local heuristic only; this is not a definitive malicious-site or reputation scan."}
    if not url:
        return {"input":"","risk_level":"Unknown","warnings":["Enter a URL."],"note":result["note"]}
    parsed=urlparse(url if "://" in url else "https://"+url)
    host=(parsed.hostname or "").lower()
    if not host:
        result["risk_level"]="Unknown"; result["warnings"].append("URL could not be parsed."); return result
    if parsed.scheme=="http": result["warnings"].append("The URL uses HTTP rather than HTTPS.")
    if "@" in parsed.netloc: result["warnings"].append("The URL contains '@', which can hide the actual destination.")
    if host.startswith("xn--") or ".xn--" in host: result["warnings"].append("The domain contains punycode; verify it carefully.")
    if len(url)>150: result["warnings"].append("The URL is unusually long.")
    if host.count("-")>=3: result["warnings"].append("The domain contains many hyphens.")
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$",host): result["warnings"].append("The destination is an IP address.")
    if len(result["warnings"])>=3: result["risk_level"]="High"
    elif result["warnings"]: result["risk_level"]="Review"
    return result

def generate_security_tips():
    tips=[
        "Use unique passwords for important accounts.",
        "Enable MFA wherever possible.",
        "Install security updates promptly.",
        "Keep protected backups of important data.",
        "Verify unexpected payment or password-reset requests.",
        "Avoid opening unexpected attachments.",
        "Check the domain before entering sensitive information.",
        "Review account login activity.",
        "Limit unnecessary app permissions.",
        "Report suspected phishing through official channels."
    ]
    return secrets.SystemRandom().sample(tips,5)
