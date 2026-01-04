from fastapi import APIRouter, HTTPException
from typing import List
import os
import json

from app.models.fighter import Fighter

router = APIRouter()


@router.get("/fighters", response_model=List[Fighter])
async def get_fighters():
    """Get list of available fighters."""
    try:
        base_path = os.getenv("DATA_PATH", "../data")
        fighters_file = f"{base_path}/fighters.json"

        # Check if fighters.json exists
        if not os.path.exists(fighters_file):
            # Return placeholder fighters if no data file exists
            return [
                Fighter(id="fighter1", name="Fighter 1", image="/fighters/fighter1.jpg"),
                Fighter(id="fighter2", name="Fighter 2", image="/fighters/fighter2.jpg"),
                Fighter(id="fighter3", name="Fighter 3", image="/fighters/fighter3.jpg"),
            ]

        # Load fighters from JSON file
        with open(fighters_file, 'r') as f:
            fighters_data = json.load(f)

        return [Fighter(**fighter) for fighter in fighters_data]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fighters/{fighter_id}", response_model=Fighter)
async def get_fighter(fighter_id: str):
    """Get details of a specific fighter."""
    fighters = await get_fighters()
    fighter = next((f for f in fighters if f.id == fighter_id), None)

    if not fighter:
        raise HTTPException(status_code=404, detail="Fighter not found")

    return fighter
