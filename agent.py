#!/usr/bin/env python3
"""
Bryan Johnson Tweet Translator
Pobiera tweety Bryana Johnsona i tłumaczy biohackerski żargon na ludzki język.

Użycie:
    python agent.py              # pobiera 5 ostatnich tweetów
    python agent.py 10           # pobiera 10 ostatnich tweetów
    python agent.py --sample     # tryb demo z przykładowymi tweetami
"""

import os
import sys
import anthropic

SYSTEM_PROMPT = """Jesteś tłumaczem specjalizującym się w dekodowaniu tweetów Bryana Johnsona.

Bryan Johnson to miliarder-biohacker znany z projektu "Blueprint" — obsesyjnego protokołu
odmładzania ciała. Jego tweety są pełne:
- Naukowego żargonu z dziedziny longevity, biohackingu i medycyny (HRV, epigenetic clock, methylation)
- Ego-mistycznych przemyśleń na temat śmierci, nieśmiertelności i ewolucji człowieka
- Danych z obsesyjnego monitorowania własnego ciała (biological age, sleep scores, biomarkers)
- Dramatycznych haseł jak "don't die", "be your own algorithm", "I don't eat, I fuel"
- Kontrowersyjnych tez podanych jako oczywiste fakty naukowe

Twoje zadanie: przetłumacz każdy tweet na prosty, ironiczny, ale merytoryczny język po polsku.

Dla każdego tweetu użyj dokładnie tego formatu:
🤖 ORYGINAŁ: [pełna treść tweeta]
🧑 PO LUDZKU: [co Bryan tak naprawdę mówi, bez żargonu, po polsku]
💊 KONTEKST: [jedno zdanie — co to oznacza w praktyce lub dlaczego to kontrowersyjne]

Bądź rzeczowy i lekko ironiczny, ale sprawiedliwy wobec merytorycznej treści naukowej.
Oddziel każdy przetłumaczony tweet linią "---"."""


def fetch_tweets(username: str = "bryan_johnson", count: int = 5) -> list[dict]:
    """Pobiera tweety używając ntscraper (bez klucza API Twitter/X)."""
    try:
        from ntscraper import Nitter
        scraper = Nitter(log_level=0, skip_instance_check=False)
        data = scraper.get_tweets(username, mode="user", number=count)
        tweets = []
        for tweet in data.get("tweets", []):
            tweets.append({
                "text": tweet.get("text", ""),
                "date": tweet.get("date", "brak daty"),
                "stats": {
                    "likes": tweet.get("stats", {}).get("likes", 0),
                    "retweets": tweet.get("stats", {}).get("retweets", 0),
                    "comments": tweet.get("stats", {}).get("comments", 0),
                },
            })
        return tweets
    except Exception as e:
        print(f"⚠️  Błąd pobierania tweetów: {e}", file=sys.stderr)
        return []


def get_sample_tweets() -> list[dict]:
    """Przykładowe tweety do trybu demo."""
    return [
        {
            "text": (
                "My biological age is 37. I am 46. I have been doing Blueprint for 2 years.\n\n"
                "I measure everything. My biomarkers are better than 99% of 18 year olds.\n\n"
                "Don't die."
            ),
            "date": "2024-01-15",
            "stats": {"likes": 12400, "retweets": 890, "comments": 340},
        },
        {
            "text": (
                "I scored 99th percentile on the epigenetic clock test. "
                "My methylation patterns suggest my immune system is 31 years old. "
                "This is what's possible when you optimize ruthlessly."
            ),
            "date": "2024-01-14",
            "stats": {"likes": 8200, "retweets": 560, "comments": 290},
        },
        {
            "text": (
                "I don't experience cravings. I don't have emotional eating. "
                "My algorithms decide what I eat.\n\n"
                "I'm not fighting my biology. I've replaced the fight with a better system."
            ),
            "date": "2024-01-13",
            "stats": {"likes": 15600, "retweets": 1200, "comments": 780},
        },
        {
            "text": (
                "Sleep is the most important thing you can do for your health. "
                "I get 8h20min per night. My HRV is 68ms. My resting heart rate is 47 bpm.\n\n"
                "Optimize sleep first. Everything else follows."
            ),
            "date": "2024-01-12",
            "stats": {"likes": 22100, "retweets": 1800, "comments": 420},
        },
        {
            "text": (
                "I spent $4M last year on Blueprint. "
                "Each dollar returned more data about human aging than anything before.\n\n"
                "We're building the manual for human existence."
            ),
            "date": "2024-01-11",
            "stats": {"likes": 9800, "retweets": 720, "comments": 510},
        },
    ]


def translate_tweets(tweets: list[dict], client: anthropic.Anthropic) -> str:
    """Używa Claude do tłumaczenia listy tweetów."""
    tweets_block = "\n\n---\n\n".join(
        f"Tweet {i + 1}:\n{t['text']}" for i, t in enumerate(tweets)
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Przetłumacz następujące tweety Bryana Johnsona na ludzki język:\n\n"
                    f"{tweets_block}"
                ),
            }
        ],
    )
    return message.content[0].text


def print_header():
    print("=" * 60)
    print("  🧬 BRYAN JOHNSON TWEET TRANSLATOR")
    print("  Biohackerski żargon → Ludzki język")
    print("=" * 60)
    print()


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Brak ANTHROPIC_API_KEY.")
        print("   Ustaw go: export ANTHROPIC_API_KEY='sk-ant-...'")
        print("   Lub skopiuj .env.example → .env i uzupełnij klucz.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    use_samples = "--sample" in sys.argv
    numeric_args = [a for a in sys.argv[1:] if not a.startswith("--")]
    count = int(numeric_args[0]) if numeric_args else 5

    print_header()

    if use_samples:
        print("📋 Tryb demo — używam przykładowych tweetów.\n")
        tweets = get_sample_tweets()[:count]
    else:
        print(f"🔍 Pobieram {count} ostatnich tweetów @bryan_johnson...\n")
        tweets = fetch_tweets("bryan_johnson", count)

        if not tweets:
            print("⚠️  Nie udało się pobrać tweetów (Twitter/X blokuje scraping).")
            print("   Przełączam na tryb demo. Użyj --sample żeby pominąć pobieranie.\n")
            tweets = get_sample_tweets()[:count]

    if not tweets:
        print("❌ Brak tweetów do przetłumaczenia.")
        sys.exit(1)

    print(f"✅ Znaleziono {len(tweets)} tweetów.\n")

    print("📊 STATYSTYKI:")
    for i, tweet in enumerate(tweets):
        s = tweet["stats"]
        print(
            f"  #{i+1} ({tweet['date']}): "
            f"❤️  {s['likes']}  🔁 {s['retweets']}  💬 {s['comments']}"
        )

    print(f"\n⏳ Tłumaczę przez Claude...\n")
    print("=" * 60)

    translated = translate_tweets(tweets, client)

    print(translated)
    print()
    print("=" * 60)
    print("  Don't die. 💊")
    print("=" * 60)


if __name__ == "__main__":
    main()
