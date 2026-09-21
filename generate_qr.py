import sys

import qrcode


def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_qr.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    img = qrcode.make(url)
    img.save("jimini_qr.png")
    print(f"Saved jimini_qr.png pointing to {url}")


if __name__ == "__main__":
    main()
