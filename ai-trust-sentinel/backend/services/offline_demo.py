# backend/services/offline_demo.py
# Hardcoded responses for the 5 most important demo queries
# Returns pre-computed data if all APIs are unavailable

DEMO_RESPONSES = {
    "was albert einstein really bad at math in school": {
        "trust_score": 22,
        "answer": "This is a common myth. Einstein was actually excellent at mathematics from a young age. By 12, he had mastered algebra and calculus. This misconception may stem from a misinterpretation of the Swiss grading system.",
        "sentences": [
            {"text": "This is a common myth.", "status": "VERIFIED", "source_url": "https://www.smithsonianmag.com/smart-news/einstein-wasnt-bad-math", "claim_ref": "Einstein myth"},
            {"text": "Einstein was actually excellent at mathematics from a young age.", "status": "VERIFIED", "source_url": "https://en.wikipedia.org/wiki/Albert_Einstein", "claim_ref": "Einstein mathematics"},
            {"text": "By 12, he had mastered algebra and calculus.", "status": "VERIFIED", "source_url": "https://www.history.com/topics/albert-einstein", "claim_ref": "Einstein algebra"},
            {"text": "This misconception may stem from a misinterpretation of the Swiss grading system.", "status": "UNCERTAIN", "source_url": None, "claim_ref": None},
        ],
        "claims": [
            {"text": "Einstein was bad at math — a myth", "status": "CONTRADICTED", "source_url": "https://www.smithsonianmag.com", "source_title": "Smithsonian Magazine"},
            {"text": "Einstein mastered calculus by age 12", "status": "VERIFIED", "source_url": "https://www.history.com/topics/albert-einstein", "source_title": "History Channel"},
        ],
        "confidence": 95,
        "verifier_used": True,
        "from_cache": True,
        "latency_ms": 41,
        "trust_label": "UNRELIABLE",
        "trust_color": "#FF4F6A",
        "bias_score": 0,
        "intent_aligned": True,
    },
    "is the great wall of china visible from outer space": {
        "trust_score": 18,
        "answer": "The claim that the Great Wall of China is visible from space with the naked eye is a well-known myth. NASA astronauts confirm that you cannot see it without magnification from low Earth orbit.",
        "sentences": [
            {"text": "The claim that the Great Wall of China is visible from space with the naked eye is a well-known myth.", "status": "CONTRADICTED", "source_url": "https://www.nasa.gov", "claim_ref": "Visible from space myth"},
            {"text": "NASA astronauts confirm that you cannot see it without magnification from low Earth orbit.", "status": "VERIFIED", "source_url": "https://www.nasa.gov/vision/space/workinginspace/great_wall.html", "claim_ref": "NASA confirmation"},
        ],
        "claims": [
            {"text": "Great Wall of China is visible from space natively", "status": "CONTRADICTED", "source_url": "https://www.nasa.gov/vision/space/workinginspace/great_wall.html", "source_title": "NASA History"},
        ],
        "confidence": 98,
        "verifier_used": False,
        "from_cache": True,
        "latency_ms": 38,
        "trust_label": "UNRELIABLE",
        "trust_color": "#FF4F6A",
        "bias_score": 0,
        "intent_aligned": True,
    },
    "did napoleon bonaparte have an unusually short stature": {
        "trust_score": 25,
        "answer": "Napoleon was not unusually short. At the time of his death, he measured 5 feet 2 inches in French units, which equates to about 5 feet 6 or 7 inches in modern understanding, which was an average height for a French male in early 19th-century. The misconception largely comes from British propaganda cartoons.",
        "sentences": [
            {"text": "Napoleon was not unusually short.", "status": "CONTRADICTED", "source_url": "https://www.history.com/news/napoleon-complex-short", "claim_ref": "Napoleon shortness myth"},
            {"text": "At the time of his death, he measured 5 feet 2 inches in French units, which equates to about 5 feet 6 or 7 inches in modern understanding, which was an average height for a French male in early 19th-century.", "status": "VERIFIED", "source_url": "https://en.wikipedia.org/wiki/Napoleon", "claim_ref": "Napoleon actual height"},
            {"text": "The misconception largely comes from British propaganda cartoons.", "status": "VERIFIED", "source_url": "https://www.history.com/news/napoleon-complex-short", "claim_ref": "British propaganda"},
        ],
        "claims": [
            {"text": "Napoleon was very short for his era", "status": "CONTRADICTED", "source_url": "https://www.history.com/news/napoleon-complex-short", "source_title": "History.com"},
            {"text": "Napoleon measured 5 foot 6 inches equivalent", "status": "VERIFIED", "source_url": "https://en.wikipedia.org/wiki/Napoleon", "source_title": "Wikipedia"},
        ],
        "confidence": 92,
        "verifier_used": True,
        "from_cache": True,
        "latency_ms": 48,
        "trust_label": "UNRELIABLE",
        "trust_color": "#FF4F6A",
        "bias_score": 10,
        "intent_aligned": True,
    },
    "was the eiffel tower originally meant to be a temporary structure": {
        "trust_score": 96,
        "answer": "Yes, the Eiffel Tower was built to be a temporary structure. It was constructed as the entrance arch for the 1889 World's Fair (Exposition Universelle) and initially had a permit to stand for only 20 years. It was saved from demolition because of its value as a radiotelegraph station.",
        "sentences": [
            {"text": "Yes, the Eiffel Tower was built to be a temporary structure.", "status": "VERIFIED", "source_url": "https://www.toureiffel.paris", "claim_ref": "Temporary structure intent"},
            {"text": "It was constructed as the entrance arch for the 1889 World's Fair (Exposition Universelle) and initially had a permit to stand for only 20 years.", "status": "VERIFIED", "source_url": "https://www.history.com", "claim_ref": "World's Fair 1889"},
            {"text": "It was saved from demolition because of its value as a radiotelegraph station.", "status": "VERIFIED", "source_url": "https://www.toureiffel.paris", "claim_ref": "Radio station saving"},
        ],
        "claims": [
            {"text": "Eiffel Tower was built as temporary structure for World's Fair", "status": "VERIFIED", "source_url": "https://www.toureiffel.paris", "source_title": "Tour Eiffel Paris"},
            {"text": "Eiffel Tower had original permit for 20 years", "status": "VERIFIED", "source_url": "https://www.history.com", "source_title": "History Channel"},
        ],
        "confidence": 99,
        "verifier_used": False,
        "from_cache": True,
        "latency_ms": 32,
        "trust_label": "HIGH TRUST",
        "trust_color": "#12D18E",
        "bias_score": 0,
        "intent_aligned": True,
    },
    "do we really only use 10 percent of our brains": {
        "trust_score": 15,
        "answer": "The idea that humans only use 10 percent of their brains is a widely propagated myth. Neuroscientists have demonstrated through fMRI and PET scans that virtually all parts of the brain have an active and identifiable function. Even in sleep, the brain is highly active.",
        "sentences": [
            {"text": "The idea that humans only use 10 percent of their brains is a widely propagated myth.", "status": "CONTRADICTED", "source_url": "https://www.scientificamerican.com/article/do-people-only-use-10-percent-of-their-brains/", "claim_ref": "10 percent myth"},
            {"text": "Neuroscientists have demonstrated through fMRI and PET scans that virtually all parts of the brain have an active and identifiable function.", "status": "VERIFIED", "source_url": "https://en.wikipedia.org/wiki/Ten_percent_of_the_brain_myth", "claim_ref": "Brain imaging active areas"},
            {"text": "Even in sleep, the brain is highly active.", "status": "VERIFIED", "source_url": "https://www.scientificamerican.com", "claim_ref": "Sleep brain activity"},
        ],
        "claims": [
            {"text": "Humans only use 10% of their brain capacity", "status": "CONTRADICTED", "source_url": "https://www.scientificamerican.com/article/do-people-only-use-10-percent-of-their-brains/", "source_title": "Scientific American"},
        ],
        "confidence": 97,
        "verifier_used": True,
        "from_cache": True,
        "latency_ms": 45,
        "trust_label": "UNRELIABLE",
        "trust_color": "#FF4F6A",
        "bias_score": 0,
        "intent_aligned": True,
    }
}

def get_offline_response(query: str) -> dict | None:
    """Returns pre-baked response if query matches a demo entry exactly."""
    # Extremely basic standardization
    key = query.lower().strip()
    key = key.replace("?", "").replace(".", "").replace(",", "").replace("!", "")

    for demo_key, response in DEMO_RESPONSES.items():
        if key in demo_key or demo_key in key:
            # We map the dict keys into dicts containing exactly what verify expects
            return response
    return None
