def generate_response(image_label, image_conf, user_text=None):

    if not image_label and not user_text:
        return "Please upload an image or ask a question."

    response = ""

    # Describe image
    if image_label:
        response += f"This looks like a '{image_label}' (confidence: {image_conf}%).\n\n"

    if not user_text:
        response += "You can ask any question related to this image."
        return response

    question = user_text.lower()

    # -------- FOOD LOGIC -------- #
    if image_label in ["pizza", "burger", "sandwich", "hotdog"]:
        if "healthy" in question:
            response += "It may not be considered very healthy due to high calories and fats."
        elif "price" in question or "expensive" in question:
            response += "The price depends on restaurant and ingredients."
        elif "good" in question:
            response += "It is generally tasty and popular among many people."
        else:
            response += "It is a food item suitable for eating."

    # -------- ELECTRONICS LOGIC -------- #
    elif image_label in ["laptop", "keyboard", "mouse", "monitor", "digital_watch"]:
        if "price" in question or "expensive" in question:
            response += "The cost depends on brand, specifications, and features."
        elif "good" in question:
            response += "It can be a good choice depending on its specifications."
        elif "battery" in question:
            response += "Battery performance varies by model and usage."
        else:
            response += "It is an electronic device used for practical purposes."

    # -------- CLOTHING LOGIC -------- #
    elif image_label in ["jean", "shirt", "sneaker", "shoe"]:
        if "comfortable" in question:
            response += "Comfort depends on material and fitting."
        elif "office" in question:
            response += "It may or may not be suitable for office depending on style."
        elif "running" in question:
            response += "If designed for sports, it can be suitable for running."
        else:
            response += "It is wearable clothing or footwear."

    # -------- GENERAL LOGIC -------- #
    else:
        if "what" in question:
            response += f"It appears to be a {image_label}."
        elif "use" in question:
            response += f"This {image_label} is generally used for its primary purpose."
        elif "good" in question:
            response += "It seems useful based on its appearance."
        else:
            response += "It appears to be a useful item."

    return response