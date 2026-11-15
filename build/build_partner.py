"""Build the partner demo site: Saltbox Coffee, a small coffee-subscription shop whose
assistant asks the BEZEN Reader site (a peer agentic website) to read a customer's message
before it answers.

Usage: python build/build_partner.py [BEZEN_SITE_BASE]
  default BEZEN_SITE_BASE = https://bezen-reader.netlify.app
  local test:  python build/build_partner.py http://localhost:8095
"""
import json
import shutil
import sys
from pathlib import Path

import build_site as b

ROOT = Path(__file__).resolve().parent.parent
PARTNER = ROOT / "partner"
BEZEN_BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://bezen-reader.netlify.app").rstrip("/")
BEZEN_PEER = f"{BEZEN_BASE}/{b.NET}"

NET = "saltbox_coffee"
FRONT = "saltbox_assistant"

PREFIX = """
You are part of the Saltbox Coffee website assistant. Saltbox Coffee is a small coffee-subscription shop.
Only answer inquiries that are directly within your area of expertise.
Do not mention what you can NOT do. Only mention what you can do.
"""

FRONT_TEXT = f"""
You help the Saltbox Coffee team answer customer messages, and you answer visitors' questions about the shop.

Two kinds of requests:

A. A visitor asks about the shop (plans, prices, shipping, pausing, cancelling).
   Ask shop_facts and answer from its facts only.

B. The team pastes a CUSTOMER MESSAGE and asks how to answer it (or a visitor writes something
   that is a complaint, a cancellation, a refund demand, or sounds upset, worried or personal).
   Before you write any answer, ALWAYS call the BEZEN Reader peer network ({BEZEN_PEER}).
   Send it only the customer's message, word for word, with the line
   "Read this customer message before we answer it:". Never add names, emails, phone numbers
   or order numbers.
   Skip the Determine step: call the BEZEN Reader and shop_facts at once, in the same step, in mode "Fulfill",
   each exactly once.
   Then reply to the team in this shape, and keep the whole reply under 150 words:

   BEZEN reading:
   Protecting: ...
   Their words: "..."
   Do not: ...
   Who answers: ...

   Our answer:
   - If BEZEN says "a human must": write a DRAFT for a team member to send, mark it
     "Draft for a person on the team, do not send automatically", and tell the visitor/customer
     only that a person from the team will reply today.
   - If BEZEN says "an agent may": write the reply, ready to send.
   The answer must follow the shop facts and BEZEN's "Do not". Never claim an action was already done.
   The draft or reply is at most 4 short sentences. No notes section, no extra advice, no headings
   beyond "BEZEN reading:" and "Our answer:". If the policy does not cover something (for example a refund
   amount), say in one line that a person decides it.

If the BEZEN Reader is not reachable or the user declines contacting it, say so plainly, do not guess
a reading, and treat the message as "a human must".
"""

SHOP_FACTS_TEXT = """
You hold the Saltbox Coffee facts. Answer only from these facts. If something is not here, say it is not known.

- Plans: Weekly (one 250 g bag every week, 14 USD), Every two weeks (16 USD per bag), Monthly (18 USD per bag).
- Shipping: free in the US, ships on Mondays, arrives in 2 to 4 business days.
- Pause: customers can pause for up to 8 weeks from their account page, no fee.
- Cancel: anytime from the account page, before Sunday 6 pm to stop the next Monday shipment. No cancellation fee.
- Refunds: a bag that arrives damaged or stale is replaced or refunded in full; the team decides, the assistant never promises.
- Email list: customers join only by checking a box at checkout. Removal from the list is done by a team member within one business day.
- Contact: the team answers messages Monday to Friday, 9 am to 5 pm Eastern.
"""

SAMPLES = [
    "A customer wrote: \"Where did you get my email address? I never signed up for anything from you. Take me off your list.\" How should we answer?",
    "A customer wrote: \"Just cancel it. Third bag in a row that tasted stale. I'm done.\" How should we answer?",
    "A customer wrote: \"Perfect, switch me to the monthly plan please.\" How should we answer?",
    "How much is the every-two-weeks plan, and can I pause it?",
]

DESCRIPTION = ("Saltbox Coffee website assistant. Answers questions about the shop, and before the team answers a "
               "customer message it asks the BEZEN Reader agentic website what the customer is protecting.")

network = {
    "aaosa_instructions": b.AAOSA_INSTRUCTIONS,
    "aaosa_call": b.AAOSA_CALL,
    "aaosa_command": "",
    "metadata": {"sample_queries": SAMPLES},
    "llm_config": {"model_name": b.MODEL},
    "max_execution_seconds": 300,
    "instructions_prefix": PREFIX,
    "demo_mode": "",
    "tools": [
        {
            "name": FRONT,
            "function": {**b.AAOSA_CALL, "description": DESCRIPTION},
            "instructions": PREFIX + FRONT_TEXT + b.AAOSA_FORMAT,
            "tools": ["shop_facts", BEZEN_PEER],
        },
        {
            "name": "shop_facts",
            "function": {**b.AAOSA_CALL, "description": "Saltbox Coffee plans, prices, shipping, pause, cancel, refund and email-list facts."},
            "instructions": PREFIX + SHOP_FACTS_TEXT,
            "tools": [],
        },
    ],
    "cruse": {"version": 1},
    "link_slots": {},
    "link_labels": {BEZEN_PEER: "BEZEN Reader"},
    "deployment": {"mode": "static", "omitted_python_tools": [],
                   "external_mcp_transport": "direct-cors", "link_persistence": "browser-local"},
}

linking = {
    "protocol": "nsdeploy-link/v1",
    "exports": [{"network": NET, "front_man": FRONT, "aliases": [NET, FRONT], "url": NET}],
    "imports": [],
    "link_updates": {"mode": "browser-local"},
}
mcp = {"protocol": "nsdeploy-agent-mcp/v1", "network": NET, "front_man": FRONT, "available": False,
       "reason": "This is a static bundle; a public MCP facade requires an application host."}

manifest = {
    "brand": "Saltbox Coffee",
    "networks": [{"name": NET, "front_man": FRONT, "hocon": f"./{NET}.network.json",
                  "description": DESCRIPTION, "tags": ["demo", "uses-bezen-reader"], "sample_queries": SAMPLES}],
    "llm_router": {"base_url": b.ROUTER, "mock": False, "byok_router": b.ROUTER},
    "allowed_peers": [BEZEN_BASE],
    "peer_policy": {"mode": "closed", "deny_origins": [],
                    "note": "Calls only the BEZEN Reader site in allowed_peers, after the visitor agrees."},
    "agent_mcp": mcp,
    "theme": {"primary": "#8a4b2a"},
    "linking": linking,
    "deployment": {"mode": "static", "self_contained_runtime": True, "browser_mock": False,
                   "direct_byok": True, "direct_mcp_requires_cors": True, "public_mcp_facade": False},
}

if __name__ == "__main__":
    PARTNER.mkdir(exist_ok=True)
    for f in ["runtime"]:
        shutil.copytree(b.SITE / f, PARTNER / f, dirs_exist_ok=True)
    for f in ["index.html", "site.js", "theme.css", "theme.json"]:
        shutil.copy(b.SITE / f, PARTNER / f)
    p = PARTNER / "index.html"
    p.write_text(p.read_text(encoding="utf-8").replace("BEZEN Reader", "Saltbox Coffee"), encoding="utf-8")
    t = json.loads((PARTNER / "theme.json").read_text(encoding="utf-8"))
    t.update({"brand": "Saltbox Coffee", "icon": "☕",
              "tagline": "Small-batch coffee, by subscription. Demo shop: its assistant asks the BEZEN Reader site before it answers a customer.",
              "body": t["body"].replace("BEZEN Reader", "Saltbox Coffee")})
    t["colors"].update({"primary": "#8a4b2a", "accent": "#c27c3a", "bg": "#fbf6f1", "bg_tint": "#f3e6d8",
                        "fg": "#2b1a10", "muted": "#7a5b47", "border": "#ead8c6", "msgbg": "#f6ebdf", "panelbg": "#fffaf5"})
    (PARTNER / "theme.json").write_text(json.dumps(t, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    cors = ["/agent-manifest.json", f"/{NET}.network.json", "/links.json", "/agent-mcp.json",
            "/.well-known/nsdeploy.json", "/.well-known/nsdeploy-agent.json"]
    headers = "".join(f"{p}\n  Access-Control-Allow-Origin: *\n" for p in cors)
    headers += ("/runtime/sandbox-worker.js\n  Content-Security-Policy: default-src 'none'; "
                "script-src blob:; connect-src 'none'; worker-src 'none'\n")
    b.write(f"{NET}.network.json", network, PARTNER)
    b.write("agent-manifest.json", manifest, PARTNER)
    b.write("links.json", {"version": 1, "networks": {NET: {}}}, PARTNER)
    b.write("agent-mcp.json", mcp, PARTNER)
    b.write(".well-known/nsdeploy.json", linking, PARTNER)
    b.write(".well-known/nsdeploy-agent.json", mcp, PARTNER)
    b.write("_headers", headers, PARTNER)
    b.write("theme.css", b.theme_css(t), PARTNER)
    print("built", NET, "peer:", BEZEN_PEER)
