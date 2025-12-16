def encode(text: str, **kwargs) -> list[int]:
    return [int(len(w) / 3.5) for w in text.split(" ")]
