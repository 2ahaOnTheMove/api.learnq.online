@staticmethod
def format_pydantic_error(error):
    formatted = {}
    for item in error.errors():
        location = item.get("loc", ())
        if location:
            field = location[0]
        else:
            field = "non_field_errors"
        message = item.get("msg", "Invalid value.")
        if message.startswith("Value error, "):
            message = message.removeprefix("Value error, ")
        formatted.setdefault(field, []).append(message)
    return formatted
