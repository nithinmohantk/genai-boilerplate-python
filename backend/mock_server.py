#!/usr/bin/env python3
"""
Simple mock theme server for testing frontend theme system
"""

import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock theme data
MOCK_THEMES = [
    {
        "id": "modern-purple",
        "name": "modern_purple",
        "display_name": "Modern Purple",
        "description": "A sleek modern theme with purple accents",
        "category": "Modern",
        "color_scheme": {
            "light": {
                "primary": "#8b5cf6",
                "secondary": "#a855f7",
                "background": "#f8fafc",
                "text": "#1e293b"
            },
            "dark": {
                "primary": "#c084fc",
                "secondary": "#a78bfa",
                "background": "#0f172a",
                "text": "#f1f5f9"
            }
        }
    },
    {
        "id": "ocean-blue",
        "name": "ocean_blue",
        "display_name": "Ocean Blue",
        "description": "Deep blue theme inspired by ocean depths",
        "category": "Nature",
        "color_scheme": {
            "light": {
                "primary": "#0ea5e9",
                "secondary": "#06b6d4",
                "background": "#f0f9ff",
                "text": "#0c4a6e"
            },
            "dark": {
                "primary": "#38bdf8",
                "secondary": "#22d3ee",
                "background": "#082f49",
                "text": "#e0f2fe"
            }
        }
    },
    {
        "id": "sunset-orange",
        "name": "sunset_orange",
        "display_name": "Sunset Orange",
        "description": "Warm orange theme reminiscent of sunset",
        "category": "Nature",
        "color_scheme": {
            "light": {
                "primary": "#f97316",
                "secondary": "#fb923c",
                "background": "#fefaf5",
                "text": "#9a3412"
            },
            "dark": {
                "primary": "#fb923c",
                "secondary": "#fbbf24",
                "background": "#431407",
                "text": "#fed7aa"
            }
        }
    },
    {
        "id": "forest-green",
        "name": "forest_green",
        "display_name": "Forest Green",
        "description": "Natural green theme inspired by forests",
        "category": "Nature",
        "color_scheme": {
            "light": {
                "primary": "#059669",
                "secondary": "#10b981",
                "background": "#f0fdf4",
                "text": "#064e3b"
            },
            "dark": {
                "primary": "#34d399",
                "secondary": "#6ee7b7",
                "background": "#022c22",
                "text": "#ecfdf5"
            }
        }
    },
    {
        "id": "professional-gray",
        "name": "professional_gray",
        "display_name": "Professional Gray",
        "description": "Clean professional theme with gray tones",
        "category": "Business",
        "color_scheme": {
            "light": {
                "primary": "#6b7280",
                "secondary": "#9ca3af",
                "background": "#f9fafb",
                "text": "#111827"
            },
            "dark": {
                "primary": "#9ca3af",
                "secondary": "#d1d5db",
                "background": "#111827",
                "text": "#f3f4f6"
            }
        }
    }
]

@app.get("/")
async def root():
    return {"message": "Mock theme server running"}

@app.get("/api/themes")
async def get_themes():
    """Get all available themes"""
    return {"themes": MOCK_THEMES}

@app.get("/api/themes/{theme_id}")
async def get_theme(theme_id: str):
    """Get a specific theme by ID"""
    theme = next((t for t in MOCK_THEMES if t["id"] == theme_id), None)
    if theme:
        return theme
    return {"error": "Theme not found"}, 404

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
