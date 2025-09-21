import datetime
from typing import List, Dict

# Example mapping of trends to products (using common SKUs that might exist)
TREND_PRODUCT_MAP = {
    'festival': [
        {'name': 'A3 Paper', 'sku': 'STK-003'},
        {'name': 'Ballpoint Pen Black', 'sku': 'STK-001'},
        {'name': 'Sketch Pen Set', 'sku': 'STK-005'},
        {'name': 'Color Paper Pack', 'sku': 'STK-004'}
    ],
    'school_start': [
        {'name': 'A4 Paper', 'sku': 'STK-002'},
        {'name': 'Ballpoint Pen Blue', 'sku': 'STK-006'},
        {'name': 'Pencil Box', 'sku': 'STK-007'},
        {'name': 'Notebook', 'sku': 'STK-008'}
    ],
    'exam': [
        {'name': 'A4 Paper', 'sku': 'STK-002'},
        {'name': 'Ballpoint Pen Black', 'sku': 'STK-001'},
        {'name': 'HB Pencil', 'sku': 'STK-009'},
        {'name': 'Eraser', 'sku': 'STK-010'}
    ]
}

# Example trend calendar
TREND_CALENDAR = [
    {'name': 'school_start', 'start': (6, 1), 'end': (6, 30)},  # June
    {'name': 'exam', 'start': (3, 1), 'end': (3, 31)},         # March
    {'name': 'exam', 'start': (10, 1), 'end': (10, 31)},       # October  
    {'name': 'festival', 'start': (8, 1), 'end': (11, 30)},    # Aug-Nov (extended for current date)
    {'name': 'festival', 'start': (9, 15), 'end': (9, 30)},    # Late September festivals
]

def get_current_trends(today=None) -> List[str]:
    if today is None:
        today = datetime.date.today()
    month, day = today.month, today.day
    trends = []
    for entry in TREND_CALENDAR:
        start_month, start_day = entry['start']
        end_month, end_day = entry['end']
        if (month > start_month or (month == start_month and day >= start_day)) and \
           (month < end_month or (month == end_month and day <= end_day)):
            trends.append(entry['name'])
    return list(set(trends))

def get_trend_suggestions(today=None) -> List[Dict]:
    trends = get_current_trends(today)
    suggestions = []
    for trend in trends:
        for product in TREND_PRODUCT_MAP.get(trend, []):
            suggestions.append({
                'trend': trend,
                'product': product['name'],
                'sku': product['sku'],
                'reason': f"Recommended for {trend.replace('_', ' ').title()} season"
            })
    return suggestions
