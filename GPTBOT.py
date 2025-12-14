import wx
import math
import re
from datetime import datetime
import wikipedia

# ---------------- OFFLINE KNOWLEDGE ----------------
OFFLINE_KNOWLEDGE = {
    "what is python": "Python is a high-level, interpreted programming language known for its simplicity.",
    "what is cpu": "CPU stands for Central Processing Unit. It is the brain of the computer.",
    "what is ram": "RAM is Random Access Memory. It temporarily stores data used by the computer.",
    "what is algorithm": "An algorithm is a step-by-step procedure to solve a problem.",
    "what is operating system": "An operating system manages computer hardware and software resources.",
    "what is ai": "Artificial Intelligence is the simulation of human intelligence by machines.",
    "what is machine learning": "Machine learning enables computers to learn from data without being explicitly programmed."
}

# ---------------- MATH PARSER ----------------
def parse_casual_math(text):
    text = text.lower()

    fillers = [
        "what is", "what's", "calculate", "find",
        "tell me", "please", "value of"
    ]
    for f in fillers:
        text = text.replace(f, "")

    replacements = {
        "plus": "+",
        "minus": "-",
        "times": "*",
        "multiplied by": "*",
        "x": "*",
        "divided by": "/",
        "over": "/"
    }
    for word, op in replacements.items():
        text = text.replace(word, op)

    trig = re.search(r"(sin|sine|cos|cosine|tan|tangent)\s*(of)?\s*(\d+)", text)
    if trig:
        angle = float(trig.group(3))
        if "sin" in trig.group(1):
            return math.sin(math.radians(angle))
        if "cos" in trig.group(1):
            return math.cos(math.radians(angle))
        if "tan" in trig.group(1):
            return math.tan(math.radians(angle))

    sqrt = re.search(r"(square root of|sqrt)\s*(\d+)", text)
    if sqrt:
        return math.sqrt(float(sqrt.group(2)))

    expr = re.findall(r"[0-9+\-*/().]+", text)
    if expr:
        try:
            return eval("".join(expr))
        except:
            return None

    return None

# ---------------- CHATBOT LOGIC ----------------
def get_response(user_input):
    text = user_input.strip().lower()

    # greetings
    if any(g in text for g in ["hi", "hello", "hey"]):
        return "Hey! 😊 What can I help you with?"

    # time & date
    if "time" in text:
        return datetime.now().strftime("It’s %I:%M %p right now.")

    if "date" in text or "day" in text:
        return datetime.now().strftime("Today is %A, %d %B %Y.")

    # math FIRST
    math_result = parse_casual_math(text)
    if math_result is not None:
        return f"The answer is {round(math_result, 4)}"

    # offline knowledge SECOND
    if text in OFFLINE_KNOWLEDGE:
        return OFFLINE_KNOWLEDGE[text]

    # wikipedia LAST
    try:
        return wikipedia.summary(user_input, sentences=2)
    except wikipedia.exceptions.DisambiguationError:
        return "That could mean multiple things 🤔 Try being more specific."
    except wikipedia.exceptions.PageError:
        return "I don’t have information on that yet 😅"
    except:
        return "I’m having trouble accessing the internet right now."

# ---------------- wxPYTHON GUI ----------------
class FancyChatbot(wx.Frame):

    def __init__(self):
        super().__init__(None, title="ChatBot", size=(720, 560))
        panel = wx.Panel(self)
        panel.SetBackgroundColour("#1e1e2f")

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.chat = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_NONE
        )
        self.chat.SetBackgroundColour("#282a36")
        self.chat.SetForegroundColour("#f8f8f2")
        self.chat.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS,
                                 wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        vbox.Add(self.chat, 1, wx.EXPAND | wx.ALL, 15)

        self.input = wx.TextCtrl(
            panel,
            style=wx.TE_PROCESS_ENTER | wx.BORDER_NONE
        )
        self.input.SetBackgroundColour("#44475a")
        self.input.SetForegroundColour("#f8f8f2")
        vbox.Add(self.input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)

        send_btn = wx.Button(panel, label="Send")
        send_btn.SetBackgroundColour("#6272a4")
        send_btn.SetForegroundColour("white")
        vbox.Add(send_btn, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 15)

        panel.SetSizer(vbox)

        send_btn.Bind(wx.EVT_BUTTON, self.on_send)
        self.input.Bind(wx.EVT_TEXT_ENTER, self.on_send)

        self.chat.AppendText(
            "Bot: Hey 👋\n"
            "I can do math, answer basics even offline, and look things up.\n"
            "Try:\n"
            "• what’s 2+2\n"
            "• sine of 30\n"
            "• what is cpu\n"
            "• who is einstein\n\n"
        )

        self.Show()

    def on_send(self, event):
        user_text = self.input.GetValue().strip()
        if not user_text:
            return

        self.chat.AppendText(f"You: {user_text}\n")

        try:
            reply = get_response(user_text)
            self.chat.AppendText(f"Bot: {reply}\n\n")
        except:
            self.chat.AppendText("Bot: Oops 😅 I can’t do that yet.\n\n")

        self.chat.ShowPosition(self.chat.GetLastPosition())
        self.input.Clear()

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app = wx.App()
    FancyChatbot()
    app.MainLoop()
