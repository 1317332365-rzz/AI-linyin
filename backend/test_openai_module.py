import os

from modules.doubao_client import generate_image


def main():
    api_key = os.getenv("DOUBAO_API_KEY", "")
    model = os.getenv("DOUBAO_IMAGE_MODEL", "doubao-seedream-5-0-250415")

    if not api_key:
        print("Missing DOUBAO_API_KEY. Skip image generation test.")
        return

    result = generate_image(
        api_key=api_key,
        model=model,
        prompt="A cinematic portrait with sharp details and natural lighting",
        size="1024x1024",
    )
    print(result)


if __name__ == "__main__":
    main()
