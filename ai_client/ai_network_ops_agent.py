import os, json
from typing import Any, Dict, List
from dotenv import load_dotenv
from openai import OpenAI
from netmiko import ConnectHandler
from device_inventory import devices

# RAG
from ai_client.rag.rag_client import retrieve as rag_retrieve

load_dotenv()

# ---- tools (read-only) ----
def _connect_and_run(ip, user, pwd, cmd):
    try:
        with ConnectHandler(
            device_type="cisco_xr", 
            host=ip, 
            username=user, 
            password=pwd, 
            port=22, 
            timeout=60,  # Increased timeout
            banner_timeout=30,  # Banner read timeout
            auth_timeout=30,  # Authentication timeout
            conn_timeout=20  # Initial connection timeout
        ) as nc:
            return nc.send_command(cmd, read_timeout=90)
    except Exception as e:
        return f"❌ Error connecting to {ip}: {str(e)[:100]}"

def list_devices():
    if not devices: return "No devices configured."
    return "\n".join([f"{n} — {i['ip']} ({i['device_type']})" for n,i in devices.items()])

def show_version(name):
    info = devices.get(name); 
    return _connect_and_run(info["ip"], info["username"], info["password"], "show version") if info else f"{name} not found"

def show_interfaces(name):
    info = devices.get(name); 
    return _connect_and_run(info["ip"], info["username"], info["password"], "show interfaces") if info else f"{name} not found"

def run_command(name, cmd):
    if any(x in cmd.lower() for x in ["configure","reload","commit","shutdown","copy ","write "]):
        return "⚠️ Refused: risky commands disallowed in training."
    info = devices.get(name); 
    return _connect_and_run(info["ip"], info["username"], info["password"], cmd) if info else f"{name} not found"

# ---- Agent ----
CORE_SYSTEM = (
    "You are a NetworkOps agent with a retrieve-plan-act-reflect loop.\n"
    "1) Use retrieved RAG context to ground advice.\n"
    "2) Prefer read-only show commands.\n"
    "3) Ask for a device if missing; never assume.\n"
    "4) Refuse risky commands.\n"
)

class Agent:
    def __init__(self):
        api = os.getenv("OPENAI_API_KEY") or ""
        if not api: raise SystemExit("OPENAI_API_KEY missing")
        self.llm = OpenAI(api_key=api)
        self.hist: List[Dict[str, Any]] = []

    def tool_defs(self):
        return [
          {"type":"function","function":{"name":"list_devices","description":"List inventory","parameters":{"type":"object","properties":{}}}},
          {"type":"function","function":{"name":"show_version","description":"Show OS version","parameters":{"type":"object","properties":{"device_name":{"type":"string"}},"required":["device_name"]}}},
          {"type":"function","function":{"name":"show_interfaces","description":"Show interfaces","parameters":{"type":"object","properties":{"device_name":{"type":"string"}},"required":["device_name"]}}},
          {"type":"function","function":{"name":"run_command","description":"Run safe show command","parameters":{"type":"object","properties":{"device_name":{"type":"string"},"command":{"type":"string"}},"required":["device_name","command"]}}},
        ]

    def dispatch(self, fn, args):
        if fn == "list_devices": return list_devices()
        if fn == "show_version": return show_version(args["device_name"])
        if fn == "show_interfaces": return show_interfaces(args["device_name"])
        if fn == "run_command": return run_command(args["device_name"], args["command"])
        return f"unknown tool {fn}"

    def plan_act(self, user_msg: str, rag_hits: List[str]) -> str:
        # Attach RAG “footnotes” as lightweight context
        rag_note = f"RAG context (IDs): {', '.join(rag_hits) if rag_hits else 'none'}"
        self.hist.append({"role":"user","content":user_msg})
        self.hist.append({"role":"system","content":f"{CORE_SYSTEM}\n{rag_note}"})

        while True:
            resp = self.llm.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.hist,
                tools=self.tool_defs(),
                tool_choice="auto"
            )
            msg = resp.choices[0].message
            if not getattr(msg, "tool_calls", None):
                final = msg.content or "(no response)"
                self.hist.append({"role":"assistant","content":final})
                return final

            for tc in msg.tool_calls:
                fn = tc.function.name
                args = json.loads(tc.function.arguments or "{}")
                print(f"→ tool: {fn} {args}")
                result = self.dispatch(fn, args)

                self.hist.append({
                    "role":"assistant",
                    "content":None,
                    "tool_calls":[{"id":tc.id,"type":"function","function":{"name":fn,"arguments":json.dumps(args)}}]
                })
                self.hist.append({
                    "tool_call_id":tc.id,
                    "role":"tool",
                    "name":fn,
                    "content":str(result)
                })

    def process(self, q: str) -> str:
        # 1) RETRIEVE
        hits = rag_retrieve(q)  # [(id, source), ...]
        hit_ids = [h[0] for h in hits]
        # 2) PLAN + ACT (tools) + REFLECT (LLM)
        return self.plan_act(q, hit_ids)

    def chat(self):
        print("Agentic NetOps (RAG + Tools). 'quit' to exit.")
        while True:
            q = input("You: ").strip()
            if q.lower() in ("quit","exit"): break
            try:
                a = self.process(q)
                print(f"\nAgent: {a}\n")
            except Exception as e:
                print(f"\n[Error] {e}\n")

if __name__ == "__main__":
    Agent().chat()
