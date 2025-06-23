from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

KEYBOARDS = {
    "start_inline": InlineKeyboardMarkup([
        [InlineKeyboardButton(text="➕ افزودن به گروه", url="https://t.me/gift_notifier_robot?startgroup=new")]
    ]),
    "start_reply": ReplyKeyboardMarkup([
        ["🛒 تهیه اشتراک", "👤 پشتیبانی"],
        ["ℹ️ اطلاعات کاربر", "💡 راهنما"]
    ], resize_keyboard=True),
    "cancel": InlineKeyboardMarkup([
        [InlineKeyboardButton(text="❌ لغو", callback_data="cancel")]
    ]),
    "select_subscription_count": InlineKeyboardMarkup([
    [
        InlineKeyboardButton("تعداد", callback_data="ignore"),
        InlineKeyboardButton("قیمت با تخفیف", callback_data="ignore"),
        InlineKeyboardButton("مقدار تخفیف", callback_data="ignore")
    ],
    [
        InlineKeyboardButton("1", callback_data="sub_1"),
        InlineKeyboardButton("30 stars", callback_data="sub_1"),
        InlineKeyboardButton("تخفیف ندارد", callback_data="sub_1")
    ],
    [
        InlineKeyboardButton("5", callback_data="sub_5"),
        InlineKeyboardButton("150 stars", callback_data="sub_5"),
        InlineKeyboardButton("تخفیف ندارد", callback_data="sub_5")
    ],
    [
        InlineKeyboardButton("7", callback_data="sub_7"),
        InlineKeyboardButton("210 stars", callback_data="sub_7"),
        InlineKeyboardButton("تخفیف ندارد", callback_data="sub_7")
    ],
    [
        InlineKeyboardButton("⭐ 10", callback_data="sub_10"),
        InlineKeyboardButton("270 stars", callback_data="sub_10"),
        InlineKeyboardButton("10 درصد تخفیف", callback_data="sub_10")
    ]
]),
    "pay": InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💰 پرداخت", pay=True)
        ],
        [
            InlineKeyboardButton(text="❌ لغو", callback_data="cancel_pay")
        ]
    ])
}

def get_keyboard(key: str):
    if key not in KEYBOARDS:
        raise KeyError(f"Keyboard with key '{key}' not found.")
    return KEYBOARDS[key]
