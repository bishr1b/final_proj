# style_manager.py

def get_styles(theme):
    if theme == "flatly":  # Light mode
        return {
            "sidebar_bg": "#f0f0f0",
            "sidebar_fg": "black",
            "content_bg": "white",
            "text_fg": "black",
            "tree_bg": "white",
            "tree_fg": "black",
            "header_bg": "#007bff",
            "header_fg": "white",
        }
    else:  # Dark mode (solar, darkly...)
        return {
            "sidebar_bg": "#2c2c2c",
            "sidebar_fg": "white",
            "content_bg": "#1e1e1e",
            "text_fg": "white",
            "tree_bg": "#2b2b2b",
            "tree_fg": "white",
            "header_bg": "#0056b3",
            "header_fg": "white",
        }
