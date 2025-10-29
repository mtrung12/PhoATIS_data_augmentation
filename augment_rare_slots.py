# augment_rare_slots.py (Modified)
import random

# --- Original Entity Pools (Expanded) ---
MEALS = ["bữa_sáng", "bữa_trưa", "bữa_tối", "đồ_ăn_nhẹ", "suất_ăn_chay"]
CLASS_TYPES = ["phổ_thông", "thương_gia", "hạng_nhất", "tiết_kiệm", "hạng_hai"]
AIRCRAFT_CODES = ["a320", "b737", "787", "boeing_737", "boeing_777", "a321"]
STOPLOCS = ["hà_nội", "sài_gòn", "moscow", "doha", "dubai", "bangkok", "thành_phố_hồ_chí_minh"]

# --- New Entity Pools for Rare Slots ---
STATE_NAMES = ["california", "texas", "new_york", "florida"]
STATE_CODES = ["ca", "tx", "ny", "fl"]
COUNTRY_NAMES = ["pháp", "anh", "nhật_bản", "hàn_quốc", "việt_nam"]
DAYS_CODES = ["t2_t4_t6", "t3_t5_t7", "cuối_tuần", "hàng_ngày"] # Example codes
MEAL_CODES = ["vs", "kc", "cm", "avml"] # Vegetarian, Kosher, Chicken, Asian Veg...
RELATIVE_DAYS = ["hôm_nay", "ngày_mai", "hôm_qua"]
RETURN_DAYS = ["thứ_hai", "thứ_ba", "chủ_nhật"]
RETURN_MONTHS = ["tháng_giêng", "tháng_hai", "tháng_ba"]
RETURN_DAY_NUMS = ["20", "21", "22"]

def synthesize_rare_slots():
    out = []
    
    # --- Meal examples ---
    for meal in MEALS:
        meal_toks = meal.split('_')
        meal_slots = ["B-meal_description"] + ["I-meal_description"] * (len(meal_toks) - 1)
        toks = ["chuyến", "bay", "vn123", "có", "phục_vụ"] + meal_toks + ["không"]
        slots = ["O", "O", "O", "O", "O"] + meal_slots + ["O"]
        out.append((toks, slots, "flight", "synth_meal_description"))

    # --- Class_type examples ---
    for cls in CLASS_TYPES:
        cls_toks = cls.split('_')
        cls_slots = ["B-class_type"] + ["I-class_type"] * (len(cls_toks) - 1)
        toks = ["tôi", "muốn", "vé"] + cls_toks + ["từ", "hà_nội", "đến", "đà_nẵng"]
        slots = ["O", "O", "O"] + cls_slots + ["O", "B-fromloc.city_name", "O", "B-toloc.city_name"]
        out.append((toks, slots, "flight", "synth_class_type"))

    # --- Aircraft code examples ---
    for code in AIRCRAFT_CODES:
        code_toks = code.split('_')
        code_slots = ["B-aircraft_code"] + ["I-aircraft_code"] * (len(code_toks) - 1)
        toks = ["chuyến", "bay", "đến", "huế", "sử_dụng", "máy_bay"] + code_toks
        slots = ["O", "O", "O", "B-toloc.city_name", "O", "O"] + code_slots
        out.append((toks, slots, "aircraft", "synth_aircraft_code"))

    # --- Stoploc examples ---
    for stop in STOPLOCS:
        stop_toks = stop.split('_')
        stop_slots = ["B-stoploc.city_name"] + ["I-stoploc.city_name"] * (len(stop_toks) - 1)
        toks = ["tôi", "muốn", "bay", "đến", "singapore", "với", "một", "điểm_dừng", "ở"] + stop_toks
        slots = ["O", "O", "O", "O", "B-toloc.city_name", "O", "O", "O", "O"] + stop_slots
        out.append((toks, slots, "flight", "synth_stoploc_city"))

    # --- Return Date/Time examples ---
    for day in RETURN_DAYS:
        toks = ["tôi", "muốn", "vé", "khứ_hồi", "và", "quay_về", "vào", day]
        slots = ["O", "O", "O", "B-round_trip", "O", "O", "O", "B-return_date.day_name"]
        out.append((toks, slots, "flight", "synth_return_date.day_name"))
        
    for month, day_num in zip(RETURN_MONTHS, RETURN_DAY_NUMS):
        toks = ["tôi", "cần", "vé", "khứ_hồi", "ngày", "về", "là", day_num, month]
        slots = ["O", "O", "O", "B-round_trip", "O", "O", "O", "B-return_date.day_number", "B-return_date.month_name"]
        out.append((toks, slots, "flight", "synth_return_date.day_month"))

    toks = ["chuyến", "bay", "khứ_hồi", "về", "trước", "5", "giờ", "chiều"]
    slots = ["O", "O", "B-round_trip", "O", "B-return_time.time_relative", "B-return_time.time", "I-return_time.time", "B-return_time.period_of_day"]
    out.append((toks, slots, "flight", "synth_return_time"))

    # --- State/Country examples ---
    for state, code in zip(STATE_NAMES, STATE_CODES):
        # toloc.state_name, toloc.state_code
        toks = ["chuyến", "bay", "đến", "dallas", state, code]
        slots = ["O", "O", "O", "B-toloc.city_name", "B-toloc.state_name", "B-toloc.state_code"]
        out.append((toks, slots, "flight", "synth_toloc_state"))
        
        # fromloc.state_name
        toks = ["chuyến", "bay", "từ", "austin", state, "đến", "hà_nội"]
        slots = ["O", "O", "O", "B-fromloc.city_name", "B-fromloc.state_name", "O", "B-toloc.city_name"]
        out.append((toks, slots, "flight", "synth_fromloc_state"))

    for country in COUNTRY_NAMES:
        # toloc.country_name
        toks = ["chuyến", "bay", "đến", "paris", country]
        slots = ["O", "O", "O", "B-toloc.city_name", "B-toloc.country_name"]
        out.append((toks, slots, "flight", "synth_toloc_country"))

    # --- Relative Date examples (today_relative) ---
    for rel_day in RELATIVE_DAYS:
        # depart_date.today_relative
        toks = ["tôi", "cần", "chuyến", "bay", "khởi_hành", rel_day]
        slots = ["O", "O", "O", "O", "O", "B-depart_date.today_relative"]
        out.append((toks, slots, "flight", "synth_depart_date.today_relative"))
        
        # arrive_date.today_relative
        toks = ["tôi", "muốn", "đến", "nơi", rel_day]
        slots = ["O", "O", "O", "O", "B-arrive_date.today_relative"]
        out.append((toks, slots, "flight", "synth_arrive_date.today_relative"))
        
        # return_date.today_relative
        toks = ["vé", "khứ_hồi", "về", rel_day]
        slots = ["O", "B-round_trip", "O", "B-return_date.today_relative"]
        out.append((toks, slots, "flight", "synth_return_date.today_relative"))

    # --- Days Code examples ---
    for dcode in DAYS_CODES:
        toks = ["chuyến", "bay", "này", "hoạt_động", "vào", "các_ngày", dcode]
        slots = ["O", "O", "O", "O", "O", "O", "B-days_code"]
        out.append((toks, slots, "flight", "synth_days_code"))

    # --- Meal Code examples ---
    for mcode in MEAL_CODES:
        toks = ["tôi", "muốn", "đặt", "suất_ăn", "mã", mcode]
        slots = ["O", "O", "O", "O", "O", "B-meal_code"]
        out.append((toks, slots, "meal", "synth_meal_code"))

    return out