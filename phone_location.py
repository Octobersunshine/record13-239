import json
import re
import os
from typing import Optional, Dict, Tuple


DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "area_codes.json")


class PhoneLocation:
    def __init__(self, data_file: str = DATA_FILE):
        self._area_codes = self._load_data(data_file)

    @staticmethod
    def _load_data(data_file: str) -> Dict[str, Dict]:
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def parse_phone(phone: str) -> Optional[str]:
        phone = phone.strip()
        patterns = [
            r"^0\d{2,3}-\d{7,8}$",
            r"^\(0\d{2,3}\)\d{7,8}$",
            r"^0\d{9,11}$",
        ]
        for pattern in patterns:
            if re.match(pattern, phone):
                digits = re.sub(r"\D", "", phone)
                return digits
        return None

    def extract_area_code(self, phone_digits: str) -> Tuple[Optional[str], Optional[str]]:
        if len(phone_digits) >= 3 and phone_digits[:3] in self._area_codes:
            return phone_digits[:3], phone_digits[3:]
        if len(phone_digits) >= 4 and phone_digits[:4] in self._area_codes:
            return phone_digits[:4], phone_digits[4:]
        return None, None

    def query(self, phone: str) -> Optional[Dict[str, str]]:
        digits = self.parse_phone(phone)
        if not digits:
            return None
        area_code, local_number = self.extract_area_code(digits)
        if not area_code:
            return None
        area_data = self._area_codes.get(area_code)
        if not area_data:
            return None
        province = area_data["province"]
        city = area_data["city"]
        if "prefixes" in area_data and local_number and len(local_number) >= 1:
            first_digit = local_number[0]
            city = area_data["prefixes"].get(first_digit, area_data["city"])
        return {
            "area_code": area_code,
            "province": province,
            "city": city,
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="固话号码归属地查询")
    parser.add_argument("phone", nargs="?", help="固话号码，如 010-12345678")
    parser.add_argument("-i", "--interactive", action="store_true", help="交互式模式")
    args = parser.parse_args()

    service = PhoneLocation()

    if args.interactive:
        print("固话号码归属地查询服务（输入 q 退出）")
        while True:
            try:
                phone = input("请输入固话号码: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if phone.lower() in ("q", "quit", "exit"):
                break
            result = service.query(phone)
            if result:
                print(
                    f"区号: {result['area_code']}, 省份: {result['province']}, 城市: {result['city']}"
                )
            else:
                print("未查询到归属地信息或号码格式错误")
        return

    if not args.phone:
        parser.print_help()
        return

    result = service.query(args.phone)
    if result:
        print(
            f"区号: {result['area_code']}, 省份: {result['province']}, 城市: {result['city']}"
        )
    else:
        print("未查询到归属地信息或号码格式错误")


if __name__ == "__main__":
    main()
