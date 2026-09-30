from database import get_knowledge

class CybersecurityChatbot:
    def respond(self, message):
        text = message.lower().strip()
        if any(x in text for x in ["hello","hi","hey"]):
            return "Hello! I am the Cybersecurity Awareness Assistant. Ask me about phishing, passwords, malware, MFA, ransomware, privacy, scams, or account protection."

        knowledge = get_knowledge()
        for item in knowledge:
            keywords = [x.strip().lower() for x in item["keywords"].split(",")]
            if any(k in text for k in keywords):
                return item["answer"]

        if "who are you" in text:
            return "I am a Python-based defensive cybersecurity awareness assistant."
        if "help" in text:
            return "I can explain phishing, password security, malware, ransomware, MFA, social engineering, privacy, Wi-Fi security, and account-compromise response."
        if "what is cybersecurity" in text or text == "cybersecurity":
            return "Cybersecurity is the practice of protecting systems, networks, applications, accounts, and information from unauthorized access, misuse, disruption, or damage."

        return "I do not have a matching knowledge item yet. Try a question about phishing, passwords, malware, ransomware, MFA, social engineering, or account security."
