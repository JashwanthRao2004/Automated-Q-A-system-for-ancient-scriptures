import pandas as pd
import torch, re, os, sys
from difflib import get_close_matches
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer, util

print("🔥 FINAL GITABOT (CONTEXT + CLARIFICATION + SHORT REPLIES) LOADED 🔥")

# ------------------------------------------------------
# 1️⃣ Load CSV
# ------------------------------------------------------
GITA_CSV_FILE = "bhagavad_gita_verses.csv"

if not os.path.exists(GITA_CSV_FILE):
    print(f"FATAL ERROR: '{GITA_CSV_FILE}' not found.")
    sys.exit(1)

df = pd.read_csv(GITA_CSV_FILE)
if df.empty:
    print("FATAL ERROR: Empty CSV.")
    sys.exit(1)

df["chapter_number"] = (
    df["chapter_number"]
    .astype(str)
    .str.replace(r"Chapter\s*", "", regex=True)
    .str.strip()
)

# ------------------------------------------------------
# 2️⃣ Knowledge Base
# ------------------------------------------------------
figures = {
    "krishna": "Krishna is the divine teacher of the Bhagavad Gita.",
    "arjuna": "Arjuna represents the human soul facing moral conflict.",
    "dharma": "Dharma means righteous duty and moral responsibility."
}

# ------------------------------------------------------
# 3️⃣ Conversation Memory
# ------------------------------------------------------
conversation_memory = {
    "last_topic": None,
    "awaiting_clarification": False
}

# ------------------------------------------------------
# 4️⃣ Load LLM
# ------------------------------------------------------
model_name = "microsoft/Phi-3-mini-4k-instruct"
is_dummy_model = False

print("⚙️ Loading LLM...")

try:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map=None
    )
    model.to("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    print("✅ LLM loaded successfully")
except Exception as e:
    print(f"❌ LLM failed: {e}")
    is_dummy_model = True

# ------------------------------------------------------
# 5️⃣ Load Sentence Transformer (optional)
# ------------------------------------------------------
try:
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    corpus_embeddings = embedder.encode(
        df["translation"].tolist(),
        convert_to_tensor=True,
        show_progress_bar=False
    )
except Exception:
    embedder = None
    corpus_embeddings = None

# ------------------------------------------------------
# 6️⃣ Helper Functions
# ------------------------------------------------------
def fuzzy_match(word, choices, cutoff=0.75):
    match = get_close_matches(word, choices, n=1, cutoff=cutoff)
    return match[0] if match else None

def is_short_query(text):
    keys = ["short", "brief", "simple", "define", "summary", "line"]
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return any(w in keys or fuzzy_match(w, keys) for w in words)

def extract_topic(text):
    topics = {
        "karma": ["karma", "action", "work"],
        "dharma": ["dharma", "duty"],
        "soul": ["soul", "atman"],
        "peace": ["peace", "calm"],
        "stress": ["stress", "anxiety"],
        "krishna": ["krishna", "krisna"]
    }
    words = re.findall(r"[a-zA-Z]+", text.lower())
    for topic, keys in topics.items():
        for w in words:
            if w in keys or fuzzy_match(w, keys):
                return topic
    return None

def is_topic_only_reply(text):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return len(words) == 1 and words[0] in [
        "karma", "dharma", "soul", "atman",
        "peace", "stress", "krishna"
    ]

# ------------------------------------------------------
# 7️⃣ Clarification Logic
# ------------------------------------------------------
def needs_clarification(user_text, last_topic):
    vague_words = ["it", "that", "this", "they"]
    life_words = ["help", "life", "benefit", "use", "importance"]

    if not last_topic:
        return False

    if last_topic in ["krishna", "arjuna"]:
        if any(w in user_text for w in vague_words):
            if any(w in user_text for w in life_words):
                return True

    return False

# ------------------------------------------------------
# 8️⃣ Short Answer Overrides (Authoritative)
# ------------------------------------------------------
def short_answer_override(prompt):
    p = prompt.lower()

    if "karma" in p:
        return "Karma means action and its results. One should perform duty without attachment."
    if "dharma" in p:
        return "Dharma means righteous duty and moral responsibility."
    if "soul" in p or "atman" in p:
        return "The soul is eternal and unchanging, beyond birth and death."
    if "peace" in p:
        return "Peace comes from selfless action and detachment from results."
    if "stress" in p:
        return "Stress reduces when one acts calmly without attachment to outcomes."
    if "krishna" in p:
        return "Krishna is the divine teacher of the Bhagavad Gita."

    return None

# ------------------------------------------------------
# 9️⃣ Clean Sentence Extractor (No Broken Endings)
# ------------------------------------------------------
def clean_complete_sentences(text, max_sentences=2):
    sentences = re.findall(r"[^.!?]+[.!?]", text)
    if not sentences:
        return text.strip()
    return " ".join(sentences[:max_sentences]).strip()

# ------------------------------------------------------
# 🔟 Response Generation
# ------------------------------------------------------
def generate_response(prompt, short_answer=False):
    if short_answer:
        override = short_answer_override(prompt)
        if override:
            return override

    if is_dummy_model:
        return "Please perform your duty with wisdom and detachment."

    full_prompt = (
        "Explain Bhagavad Gita teachings clearly and accurately.\n"
        f"User: {prompt}\nAssistant:"
    )

    inputs = tokenizer(full_prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=120,
            temperature=0.6,
            do_sample=True,
            repetition_penalty=1.2,
            eos_token_id=tokenizer.eos_token_id
        )

    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    answer = text.split("Assistant:")[-1].strip()

    return clean_complete_sentences(answer, 2)

# ------------------------------------------------------
# 11️⃣ Main Bot Logic
# ------------------------------------------------------
def gita_bot_response(user_input):
    u = user_input.lower().strip()

    # If user replies with topic after clarification
    if conversation_memory["awaiting_clarification"] and is_topic_only_reply(u):
        conversation_memory["awaiting_clarification"] = False
        conversation_memory["last_topic"] = u
        return short_answer_override(u)

    topic = extract_topic(u)
    if topic:
        conversation_memory["last_topic"] = topic

    # Ask clarification if needed
    if needs_clarification(u, conversation_memory["last_topic"]):
        conversation_memory["awaiting_clarification"] = True
        return (
            "Do you mean how Krishna’s teachings help in life, "
            "or how principles like karma help in life?"
        )

    # Resolve vague references
    if any(w in u for w in ["it", "that", "this"]):
        if conversation_memory["last_topic"]:
            u = f"{conversation_memory['last_topic']} {u}"

    # Direct knowledge base
    for k, v in figures.items():
        if k in u:
            return v

    short_answer = is_short_query(u)
    prompt = f"Explain in the light of Bhagavad Gita: {u}"

    return generate_response(prompt, short_answer)

# ------------------------------------------------------
# 12️⃣ CLI Test
# ------------------------------------------------------
if __name__ == "__main__":
    print("\n🕉️ GitaBot ready. Type 'exit' to quit.")
    while True:
        try:
            q = input("\nYou: ")
            if q.lower() in {"exit", "quit"}:
                print("GitaBot: Goodbye 🙏")
                break
            print("\nGitaBot:", gita_bot_response(q))
        except KeyboardInterrupt:
            print("\nGitaBot: Shanti 🙏")
            break
