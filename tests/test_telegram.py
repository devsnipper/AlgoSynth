import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import os
from dotenv import load_dotenv
import requests

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

TOKEN   = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL     = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

print("=== BLOC 8 â€” Notifications Telegram ===\n")

if not TOKEN or not CHAT_ID:
    print("ERREUR : TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID manquant dans .env")
    exit(1)

print(f"Token   : {TOKEN[:10]}...")
print(f"Chat ID : {CHAT_ID}\n")

def send(message):
    try:
        r = requests.post(URL, data={"chat_id": CHAT_ID, "text": message}, timeout=5)
        data = r.json()
        if data.get("ok"):
            print(f"  OK â€” '{message}'")
        else:
            print(f"  ERREUR â€” {data}")
    except Exception as e:
        print(f"  ERREUR â€” {e}")

print("Envoi des notifications de test...\n")

send("Bot demarre\nBalance : 9989.67 USD")
send("Trade ouvert\nBUY Crash 1000 Index.0\nEntree : 6031.691")
send("Trade ferme (GAIN)\nCrash 1000 Index.0\nProfit : +2.45\nPnL jour : +2.45")
send("Trade ferme (PERTE)\nCrash 1000 Index.0\nProfit : -1.20\nPnL jour : +1.25")
send("Spike detecte sur Boom 1000 Index.0 â€” trade skippe")
send("Bot arrete\nPnL final journalier : +1.25")

print("\nVÃ©rifie ton Telegram â€” 6 messages doivent etre arrives.")
