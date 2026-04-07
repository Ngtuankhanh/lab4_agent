import csv
import logging
import os
from typing import Dict
from langchain_core.tools import tool

# Cấu hình LOGGING
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TravelBuddyTools")


def load_flights_from_csv(file_path: str = "flights.csv") -> Dict:
    """Load flight data from CSV to a dictionary format."""
    db = {}
    if not os.path.exists(file_path):
        logger.warning(f"File {file_path} không tồn tại. Sử dụng DB trống.")
        return db

    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                origin, dest = row["origin"], row["destination"]
                key = (origin, dest)
                if key not in db:
                    db[key] = []
                # Chuyển giá sang int
                row["price"] = int(row["price"])
                db[key].append(row)
    except Exception as e:
        logger.error(f"Lỗi khi đọc file flights.csv: {e}")
    return db


def load_hotels_from_csv(file_path: str = "hotels.csv") -> Dict:
    """Load hotel data from CSV to a dictionary format."""
    db = {}
    if not os.path.exists(file_path):
        logger.warning(f"File {file_path} không tồn tại. Sử dụng DB trống.")
        return db

    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                city = row["city"]
                if city not in db:
                    db[city] = []
                # Chuyển đổi kiểu dữ liệu
                row["stars"] = int(row["stars"])
                row["price_per_night"] = int(row["price_per_night"])
                row["rating"] = float(row["rating"])
                db[city].append(row)
    except Exception as e:
        logger.error(f"Lỗi khi đọc file hotels.csv: {e}")
    return db


# Data initialization
FLIGHTS_DB = load_flights_from_csv()
HOTELS_DB = load_hotels_from_csv()


@tool
def search_flights(origin: str, destination: str) -> str:
    """
    Tìm kiếm các chuyến bay giữa hai thành phố.
    Tham số:
    - origin: thành phố khởi hành (VD: 'Hà Nội', 'Hồ Chí Minh')
    - destination: thành phố đến (VD: 'Đà Nẵng', 'Phú Quốc')
    """
    logger.info(
        f"ACTION: search_flights(origin='{origin}', destination='{destination}')"
    )

    try:
        # Validate Input
        if not origin or not destination:
            return "Lỗi: Vui lòng cung cấp cả điểm đi và điểm đến."

        flights = FLIGHTS_DB.get((origin, destination))

        # Thử tra ngược
        if not flights:
            flights = FLIGHTS_DB.get((destination, origin))
            if flights:
                origin, destination = destination, origin

        if not flights:
            obs = f"Không tìm thấy chuyến bay từ {origin} đến {destination}."
            logger.info(f"OBSERVATION: {obs}")
            return obs

        result = f"Chuyến bay từ {origin} đến {destination}:\n"
        for f in flights:
            price_fmt = f"{f['price']:,}₫".replace(",", ".")
            result += f"- {f['airline']} ({f['class']}): {f['departure']} - {f['arrival']}, Giá: {price_fmt}\n"

        logger.info(f"OBSERVATION: Tìm thấy {len(flights)} chuyến bay.")
        return result
    except Exception as e:
        err = f"Lỗi hệ thống khi tìm chuyến bay: {str(e)}"
        logger.error(f"ERROR in search_flights: {err}")
        return err


@tool
def search_hotels(city: str, max_price_per_night: int = 99999999) -> str:
    """
    Tìm kiếm khách sạn tại một thành phố, có thể lọc theo giá tối đa mỗi đêm.
    Tham số:
    - city: tên thành phố (VD: 'Đà Nẵng', 'Phú Quốc', 'Hồ Chí Minh')
    - max_price_per_night: giá tối đa mỗi đêm (VNĐ), mặc định không giới hạn
    """
    logger.info(
        f"ACTION: search_hotels(city='{city}', max_price_per_night={max_price_per_night})"
    )

    try:
        # Validate Input
        if not city or not isinstance(city, str):
            return "Lỗi: Tên thành phố không hợp lệ."

        hotels = HOTELS_DB.get(city)
        if not hotels:
            obs = f"Không tìm thấy dữ liệu khách sạn tại {city}."
            logger.info(f"OBSERVATION: {obs}")
            return obs

        filtered_hotels = [
            h for h in hotels if h["price_per_night"] <= max_price_per_night
        ]

        if not filtered_hotels:
            obs = f"Không tìm thấy khách sạn tại {city} với giá dưới {max_price_per_night:,}₫/đêm."
            logger.info(f"OBSERVATION: {obs}")
            return obs.replace(",", ".")

        sorted_hotels = sorted(filtered_hotels, key=lambda x: x["rating"], reverse=True)

        result = f"Khách sạn tại {city} (Giá tối đa {max_price_per_night:,}₫/đêm):\n".replace(
            ",", "."
        )
        for h in sorted_hotels:
            price_fmt = f"{h['price_per_night']:,}₫".replace(",", ".")
            result += f"- {h['name']} ({h['stars']} sao): {price_fmt}/đêm, Khu vực: {h['area']}, Rating: {h['rating']}\n"

        logger.info(f"OBSERVATION: Tìm thấy {len(sorted_hotels)} khách sạn.")
        return result
    except Exception as e:
        err = f"Lỗi hệ thống khi tìm khách sạn: {str(e)}"
        logger.error(f"ERROR in search_hotels: {err}")
        return err


@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """
    Tính toán ngân sách còn lại sau khi trừ các khoản chi phí.
    Tham số:
    - total_budget: tổng ngân sách ban đầu (VNĐ)
    - expenses: chuỗi mô tả các khoản chi, định dạng 'tên_khoản: số_tiền', cách nhau bởi dấu phẩy
    """
    logger.info(
        f"ACTION: calculate_budget(total_budget={total_budget}, expenses='{expenses}')"
    )

    try:
        if not expenses:
            return "Lỗi: Danh sách chi phí trống."

        expense_list = []
        total_expense = 0

        parts = [p.strip() for p in expenses.split(",")]
        for part in parts:
            if not part:
                continue
            if ":" not in part:
                return f"Lỗi định dạng: '{part}' thiếu dấu hai chấm."

            name, amount_str = part.split(":", 1)
            name = name.strip()
            amount_str = (
                amount_str.strip().replace(".", "").replace(",", "").replace("₫", "")
            )

            if not amount_str.isdigit():
                return (
                    f"Lỗi: Số tiền '{amount_str}' của '{name}' không phải là số hợp lệ."
                )

            amount = int(amount_str)
            expense_list.append((name, amount))
            total_expense += amount

        remaining = total_budget - total_expense

        result = "Bảng chi phí:\n"
        for name, amount in expense_list:
            result += f"- {name}: {amount:,}₫\n".replace(",", ".")

        result += f" Tổng chi: {total_expense:,}₫\n".replace(",", ".")
        result += f" Ngân sách: {total_budget:,}₫\n".replace(",", ".")
        result += f" Còn lại: {remaining:,}₫\n".replace(",", ".")

        if remaining < 0:
            result += f"\n⚠️ Vượt ngân sách {abs(remaining):,}₫!"

        logger.info(f"OBSERVATION: Đã tính xong. Còn lại {remaining:,}₫.")
        return result
    except Exception as e:
        err = f"Lỗi xử lý ngân sách: {str(e)}"
        logger.error(f"ERROR in calculate_budget: {err}")
        return err
