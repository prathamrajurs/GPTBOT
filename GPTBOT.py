import wx
import math
import re
import wikipedia
from datetime import datetime

# ---------------- 1. WIKI FILTER ----------------
def clean_for_wiki(text):
    text = text.lower().strip()
    text = re.sub(r'[?!.,]', ' ', text)
    
    triggers = [
        r"hey bot", r"hello", r"hi", r"help",
        r"please", r"kindly", 
        r"can you", r"could you", r"would you",
        r"tell me", r"explain", r"define", r"describe", r"search for", r"find",
        r"what is", r"what are", r"what's",
        r"who is", r"who are", r"who's", r"who won",
        r"where is", r"when was", r"how to"
    ]
    
    combined_pattern = r"^(" + "|".join(triggers) + r")\s+"
    while re.match(combined_pattern, text):
        text = re.sub(combined_pattern, "", text).strip()

    text = re.sub(r"^(the|a|an)\s+", "", text)
    return text.strip()

# ---------------- 2. SCIENTIFIC MATH ----------------
def parse_scientific_math(text):
    text = text.lower().strip()
    
    # Constants
    text = text.replace("pi", str(math.pi)).replace("tau", str(math.tau)).replace(" e ", str(math.e))

    # Factorial (5!)
    if "!" in text:
        match = re.search(r"(\d+)\s*!", text)
        if match: return math.factorial(int(match.group(1)))

    # Logarithms (log, ln)
    log_match = re.search(r"(log10|log|ln)\s*(of)?\s*\(?(\d+\.?\d*)\)?", text)
    if log_match:
        func, val = log_match.group(1), float(log_match.group(3))
        if func == "ln": return math.log(val)
        return math.log10(val)

    # Trigonometry (sin, cos, tan, asin...)
    trig = re.search(r"(asin|acos|atan|sin|cos|tan)\s*(of)?\s*\(?(-?\d+\.?\d*)\)?", text)
    if trig:
        func, val = trig.group(1), float(trig.group(3))
        if func in ["asin", "acos", "atan"]: 
            # Inverse trig returns degrees
            if func == "asin": return math.degrees(math.asin(val))
            if func == "acos": return math.degrees(math.acos(val))
            if func == "atan": return math.degrees(math.atan(val))
        else:
            # Normal trig takes degrees
            rad = math.radians(val)
            if func == "sin": return math.sin(rad)
            if func == "cos": return math.cos(rad)
            if func == "tan": return math.tan(rad)

    # Powers & Roots (2^3, sqrt 16)
    if "^" in text or "power" in text:
        match = re.search(r"(\d+\.?\d*)\s*(\^|power)\s*(\d+\.?\d*)", text)
        if match: return math.pow(float(match.group(1)), float(match.group(3)))

    sqrt_match = re.search(r"(sqrt|square root)\s*(of)?\s*\(?(\d+\.?\d*)\)?", text)
    if sqrt_match: return math.sqrt(float(sqrt_match.group(3)))

    # Basic Arithmetic fallback
    safe_expr = re.sub(r"[^0-9+\-*/().]", "", text)
    if len(safe_expr) > 0 and any(c.isdigit() for c in safe_expr):
        try: return eval(safe_expr)
        except: return None
    return None

# ---------------- 3. RESPONSE LOGIC ----------------
def get_response(user_input):
    clean = user_input.lower().strip()

    # Help Command
    if clean == "help" or clean == "commands":
        return (
            "**🤖 AVAILABLE COMMANDS:**\n"
            "-----------------------------------\n"
            "1. **Scientific Math:**\n"
            "   • Trig: sin 90, cos(0), tan 45\n"
            "   • Inverse: asin 0.5, acos 0\n"
            "   • Logs: log 100, ln 5\n"
            "   • Algebra: 5!, 2^3, sqrt 16, 50 * 5\n"
            "   • Constants: pi, e\n\n"
            "2. **Smart Knowledge:**\n"
            "   • Ask: 'Who is Python?', 'Who won world cup 2023?'\n"
            "   • Ask: 'Define Machine Learning'\n\n"
            "3. **Utilities:**\n"
            "   • Ask: 'Time' or 'Date'"
        )

    # Greetings
    if any(g in clean for g in ["hello", "hey", "hi"]):
        return "Hey! Click 'Help' to see what I can do."

    # Time/Date
    if "time" in clean: return datetime.now().strftime("It’s %I:%M %p.")
    if "date" in clean: return datetime.now().strftime("Today is %A, %B %d, %Y.")

    # Math
    try:
        res = parse_scientific_math(clean)
        if res is not None: return f"Result: {round(res, 5)}"
    except: pass

    # Wikipedia
    topic = clean_for_wiki(user_input)
    if not topic: return "Please ask a specific question."
    
    try:
        results = wikipedia.search(topic)
        if not results: return "No results found."
        summary = wikipedia.summary(results[0], sentences=3, auto_suggest=False)
        return f"**{results[0]}**:\n{summary}"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Did you mean: {', '.join(e.options[:3])}?"
    except:
        return "Internet connection required for searches."

# ---------------- 4. GUI WITH HELP BUTTON ----------------
class ScientificBot(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Scientific ChatBot", size=(720, 600))
        panel = wx.Panel(self)
        panel.SetBackgroundColour("#1e1e2f")

        vbox = wx.BoxSizer(wx.VERTICAL)

        # Chat Display
        self.chat = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_NONE)
        self.chat.SetBackgroundColour("#282a36")
        self.chat.SetForegroundColour("#f8f8f2")
        self.chat.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        vbox.Add(self.chat, 1, wx.EXPAND | wx.ALL, 15)

        # Input Box
        self.input = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER | wx.BORDER_NONE)
        self.input.SetBackgroundColour("#44475a")
        self.input.SetForegroundColour("#f8f8f2")
        vbox.Add(self.input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)

        # Button Row (Help & Send)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # Help Button
        help_btn = wx.Button(panel, label="Help ❓")
        help_btn.SetBackgroundColour("#ffb86c") # Orange/Gold for distinction
        help_btn.SetForegroundColour("black")
        hbox.Add(help_btn, 0, wx.RIGHT, 10)

        # Send Button
        send_btn = wx.Button(panel, label="Send 🚀")
        send_btn.SetBackgroundColour("#6272a4") # Dracula Purple
        send_btn.SetForegroundColour("white")
        hbox.Add(send_btn, 0)

        vbox.Add(hbox, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 15)
        panel.SetSizer(vbox)

        # Bindings
        send_btn.Bind(wx.EVT_BUTTON, self.on_send)
        help_btn.Bind(wx.EVT_BUTTON, self.on_help)
        self.input.Bind(wx.EVT_TEXT_ENTER, self.on_send)

        self.chat.AppendText("HEY HOW CAN I HELP YOU TODAY?!\n\n")
        self.Show()

    def on_send(self, event):
        user_text = self.input.GetValue().strip()
        if not user_text: return
        
        self.chat.AppendText(f"You: {user_text}\n")
        self.input.Clear()
        wx.CallAfter(self.bot_reply, user_text)

    def on_help(self, event):
        # Directly trigger the help message
        wx.CallAfter(self.bot_reply, "help")

    def bot_reply(self, text):
        reply = get_response(text)
        self.chat.AppendText(f"Bot: {reply}\n\n")

if __name__ == "__main__":
    app = wx.App()
    ScientificBot()
    app.MainLoop()
