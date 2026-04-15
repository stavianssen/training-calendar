#!/usr/bin/env python3
"""
Generate ICS calendar file from training plan CSV files.
February + March 2026 only. SWIM, STRENGTH, RUN, BIKE only (no Morning Espresso).
"""

import csv
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

# Emojis like on the screenshot
EMOJI = {"Swim": "🏊", "Bike": "🚴", "Run": "🏃", "Strength": "💪"}
LOCATION = {"Swim": "Pool", "Bike": "Trainer/Outdoor", "Run": "Outdoor", "Strength": "Home/Gym"}

# Workout library - full details from HTML app (subset for Feb-Mar)
WORKOUT_LIBRARY = {
    "swim": {
        "2100m technique": """🏊 SWIM - Technique (2100m)

WARM-UP (400m):
• 200m free, 100m back, 100m breast

DRILLS (500m):
• 4x50m catch-up
• 4x50m single arm (alt.)
• 100m fist drill

TECHNIQUE SET (600m):
• 6x100m focusing on:
  1-2: Catch phase
  3-4: Pull through
  5-6: Rotation
  (20s rest)

MAIN SET (400m):
• 8x50m descending 1-4, 5-8
  (15s rest)

COOL-DOWN (200m):
• 200m easy choice

💡 Focus: One technique element at a time.""",
        "2200m drill + endurance": """🏊 SWIM - Drill + Endurance (2200m)

WARM-UP (400m):
• 300m easy mix
• 100m kick with fins

DRILLS (400m):
• 4x100m as 50 drill / 50 swim
  Drills: catch-up, fingertip, fist, single arm

MAIN SET (1200m):
• 3x400m @ steady aerobic
  Rest: 30s
  Focus: Negative split each 400

COOL-DOWN (200m):
• 200m easy backstroke

💡 Focus: Build through each 400m. Stay relaxed.""",
        "2400m - 400m TT + 200m TT": """🏊 CSS TEST - Critical Swim Speed (2400m)

⚠️ IMPORTANT TEST - determines your training zones!

WARM-UP (600m):
• 400m easy
• 4x50m build (20s rest)

TEST SET:
• 400m TIME TRIAL - ALL OUT
  Record your time!
  Rest: 5 minutes (easy swim/float)

• 200m TIME TRIAL - ALL OUT
  Record your time!

COOL-DOWN (400m+):
• 400m+ very easy

📊 Calculate CSS:
CSS pace = (400m time - 200m time) ÷ 2
This is your threshold pace per 100m

💡 Pace yourself on 400m - don't die in last 100m!""",
        "1600m easy": """🏊 RECOVERY SWIM (1600m)

All at EASY effort today!

WARM-UP (400m):
• 400m easy mix

MAIN SET (800m):
• 400m pull - smooth and easy
• 400m swim - focus on rotation

TECHNIQUE (400m):
• 8x50m alternating drill/swim

COOL-DOWN:
• 200m choice - very easy

💡 RECOVERY WEEK - no intensity!""",
        "1800m easy": """🏊 EASY TECHNIQUE (1800m)

WARM-UP (400m):
• 400m easy mix

DRILLS (400m):
• 8x50m various drills
  - Catch-up, fingertip, single arm

MAIN SET (800m):
• 8x100m @ easy aerobic
  Focus: Smooth strokes, good rotation

COOL-DOWN (200m):
• 200m backstroke easy

💡 Easy effort today - focus on feeling the water.""",
        "2700m threshold": """🏊 SWIM - Threshold (2700m)

WARM-UP (500m):
• 300m easy
• 200m pull

THRESHOLD SET (1800m):
• 6x300m @ CSS pace
  Rest: 20s between
  Focus: Even splits!

COOL-DOWN (400m):
• 200m easy
• 200m backstroke

💡 CSS = your threshold pace from test.
Should feel "comfortably hard" - sustainable but challenging.""",
        "2500m threshold pyramid": """🏊 SWIM - Threshold Pyramid (2500m)

WARM-UP (500m):
• 300m easy
• 4x50m build

THRESHOLD PYRAMID (1600m):
• 100m @ CSS pace (15s rest)
• 200m @ CSS pace (20s rest)
• 300m @ CSS pace (25s rest)
• 400m @ CSS pace (30s rest)
• 300m @ CSS pace (25s rest)
• 200m @ CSS pace (20s rest)
• 100m @ CSS pace (15s rest)

COOL-DOWN (400m):
• 400m easy pull

💡 CSS = Critical Swim Speed (your threshold pace)
Hold consistent pace throughout pyramid.""",
        "2600m race pace": """🏊 SWIM - Race Pace (2600m)

WARM-UP (500m):
• 300m easy
• 4x50m build

RACE PACE SET (1700m):
• 4x100m @ race pace (15s rest)
• 400m steady @ just below race pace
• 4x100m @ race pace (15s rest)
• 500m continuous @ race effort

COOL-DOWN (400m):
• 400m easy

💡 Race pace = CSS +2-3 sec/100m
Practice sighting every 6-8 strokes during 500m.""",
        "2700m - 1900m straight": """🏊 RACE SIMULATION (2700m)

WARM-UP (500m):
• 300m easy
• 4x50m race pace

RACE SIMULATION (1900m):
• 1900m CONTINUOUS @ race effort
  Sight every 6-8 strokes
  Practice bilateral breathing
  No stopping!

COOL-DOWN (300m):
• 300m very easy

💡 This simulates your Half Ironman swim!
Practice nutrition timing - eat 2h before.""",
    },
    "strength": {
        "PUSH + CORE": """💪 STRENGTH - Push + Core (45min)

WARM-UP (5min):
• Arm circles, shoulder rolls
• 10 push-ups easy
• 30s plank

PUSH CIRCUIT (30min) - 3 rounds:
1. Push-ups: 15-20 reps
2. Dumbbell Shoulder Press: 12 reps
3. Dumbbell Chest Press: 12 reps
4. Tricep Dips: 12-15 reps
5. Pike Push-ups: 10 reps
Rest: 60s between rounds

CORE CIRCUIT (10min) - 2 rounds:
1. Plank: 45-60s
2. Dead Bug: 12 each side
3. Russian Twists: 20 total
4. Bird Dog: 10 each side
5. Mountain Climbers: 30s

💡 Focus: Controlled movement, full range of motion.""",
        "PUSH + CORE Light": """💪 STRENGTH LIGHT - Push + Core (35min)

⚡ RECOVERY WEEK - lighter load!

WARM-UP (5min):
• Light mobility work

PUSH CIRCUIT (20min) - 2 rounds:
1. Push-ups: 10-12 reps
2. Light Shoulder Press: 10 reps
3. Light Chest Press: 10 reps
4. Tricep Dips: 10 reps
Rest: 90s between rounds

CORE (10min) - 2 rounds:
1. Plank: 30-45s
2. Dead Bug: 8 each side
3. Bird Dog: 8 each side

💡 RECOVERY WEEK - 60% effort, focus on form.""",
        "PULL": """💪 STRENGTH - Pull (45min)

WARM-UP (5min):
• Band pull-aparts
• Arm circles
• Cat-cow stretches

PULL CIRCUIT (30min) - 3 rounds:
1. Pull-ups or Lat Pulldown: 8-12 reps
2. Bent Over Rows: 12 reps each arm
3. Face Pulls: 15 reps
4. Bicep Curls: 12 reps
5. Reverse Flyes: 12 reps
Rest: 60s between rounds

BACK HEALTH (10min):
1. Superman: 12 reps
2. Prone Y-T-W: 8 each
3. Band Pull-aparts: 15 reps
4. Foam roll upper back

💡 Counterbalance swim posture - squeeze shoulder blades!""",
        "LEGS": """💪 STRENGTH - Legs (40min)

WARM-UP (5min):
• Leg swings
• Bodyweight squats
• Lunges

LEG CIRCUIT (30min) - 3 rounds:
1. Goblet Squats: 15 reps
2. Romanian Deadlifts: 12 reps
3. Walking Lunges: 12 each leg
4. Step-ups: 10 each leg
5. Calf Raises: 20 reps
6. Single Leg Glute Bridge: 12 each
Rest: 60s between rounds

STABILITY (5min):
1. Single leg stand: 30s each
2. Pistol squat progression: 5 each

💡 Triathlon-specific leg strength - single leg work is key!""",
        "LEGS light": """💪 STRENGTH LIGHT - Legs (35min)

⚡ RECOVERY WEEK - maintain, don't strain!

WARM-UP (5min):
• Light mobility

LEG CIRCUIT (25min) - 2 rounds:
1. Bodyweight Squats: 15 reps
2. Light RDL: 10 reps
3. Lunges: 8 each leg
4. Step-ups: 8 each leg
5. Calf Raises: 15 reps
Rest: 90s between rounds

MOBILITY (5min):
• Hip flexor stretch
• Pigeon pose
• Quad stretch

💡 RECOVERY - focus on mobility over load.""",
    },
    "bike": {
        "Long endurance ROUVY": """🚴 BIKE - Long Endurance ROUVY (75min)

WARM-UP (10min):
• Easy spinning, gradually increase

MAIN SET (55min):
• Choose scenic ROUVY route
• Zone 2 effort - conversational pace
• Cadence: 85-95 rpm
• Stay seated on climbs

COOL-DOWN (10min):
• Easy spinning

💡 Foundation endurance - don't go too hard!
Hydrate: 500ml+ fluid, consider 1 gel if >60min.""",
        "Long endurance": """🚴 BIKE - Long Endurance (varies)

WARM-UP (10min):
• Easy spinning

MAIN SET:
• Zone 2 steady effort
• Cadence: 85-95 rpm
• Practice race position
• Every 20min: 30s standing

COOL-DOWN (10min):
• Easy spinning

💡 Build aerobic base. Keep HR in Zone 2.
Nutrition: Hydrate every 15min, fuel every 45min.""",
        "Long + hills": """🚴 BIKE - Long with Hills (90-120min)

WARM-UP (15min):
• Easy spinning

MAIN SET:
• Undulating ROUVY route OR outdoor hills
• Zone 2 on flats
• Zone 3-4 on climbs (stay seated)
• Recover to Zone 2 on descents
• Cadence: 70-80 on climbs, 90+ on flats

COOL-DOWN (10min):
• Easy spinning

💡 Hill practice for race course!
On climbs: steady effort, don't surge.""",
        "3h+ long ride": """🚴 BIKE - Long Ride (3+ hours)

WARM-UP (15min):
• Easy spinning

MAIN SET (150min+):
• Zone 2 primary
• Practice race position
• Every 30min: 1 min standing
• Practice nutrition timing:
  - Drink every 15min
  - Gel/bar every 45min

COOL-DOWN (15min):
• Very easy spinning

💡 Race simulation! This is your 90km practice.
Mental focus: break into 30min segments.""",
        "Easy ROUVY": """🚴 RECOVERY BIKE - Easy ROUVY (55min)

⚡ RECOVERY WEEK!

EASY EFFORT:
• Choose flat, scenic route
• Zone 1-2 only
• High cadence: 90-100 rpm
• Spin the legs out

💡 RECOVERY - flush the legs, nothing more!""",
        "Easy endurance": """🚴 EASY ENDURANCE (60min)

WARM-UP (10min):
• Very easy spinning

MAIN SET (40min):
• Zone 2 steady
• Stay comfortable
• Practice position

COOL-DOWN (10min):
• Very easy

💡 Easy effort today - build consistency.""",
        "ROUVY + hills + PULL": """🚴 ROUVY HILLS + PULL (135min)

BIKE - Hilly ROUVY (90min):
• Choose hilly route
• Z2 on flats
• Z3-4 on climbs
• Practice steady climbing power

Then: PULL STRENGTH (30min)

💡 Hill-specific training for race prep!""",
        "3x12min @ SS + PULL": """🚴 SWEET SPOT + PULL (120min)

BIKE - Sweet Spot (75min):

WARM-UP (15min):
• Easy progressive spinning

MAIN SET (45min):
• 3x12min @ Sweet Spot (88-94% FTP)
  - Cadence: 85-95
  - Seated position
  - Rest: 5min easy between

COOL-DOWN (15min):
• Easy spinning

Then: PULL STRENGTH (30min)

💡 Sweet Spot = sustainable power just below threshold.""",
        "6x5min @ 90% FTP + PULL": """🚴 HILL REPEATS + PULL (125min)

BIKE - Hill Repeats (80min):

WARM-UP (15min):
• Progressive

MAIN SET (50min):
• 6x5min @ 90% FTP
  - Simulate climbing
  - Cadence: 70-80
  - Stay seated
  - Rest: 3min easy between

COOL-DOWN (15min):
• Easy spinning

Then: PULL STRENGTH (30min)

💡 Race simulation for hilly courses!""",
        "Long with climbs": """🚴 BIKE - Long with Climbs (130min)

WARM-UP (15min):
• Easy to moderate

MAIN SET (100min):
• Find climbing route
• Z2 effort on flats
• Z3-4 effort on climbs
• Practice staying seated
• Focus on steady power

COOL-DOWN (15min):
• Easy spinning, stretch after

💡 90km race prep! Practice nutrition strategy.""",
        "2x20min @ FTP + PULL": """🚴 THRESHOLD BLOCKS + PULL (130min)

BIKE - Threshold (85min):

WARM-UP (15min):
• Progressive, include 2x1min fast

MAIN SET (50min):
• 2x20min @ FTP (100%)
  - Steady power
  - Cadence: 85-95
  - Rest: 5min easy between

COOL-DOWN (15min):
• Easy spinning

Then: PULL STRENGTH (30min)

💡 FTP work - race power sustainability!""",
        "Long + race pace": """🚴 LONG + RACE PACE (135min)

WARM-UP (15min):
• Progressive

MAIN SET (105min):
• Z2 base effort
• Every 20min: 5min @ race watts
• Practice race position
• Full nutrition protocol

COOL-DOWN (15min):
• Easy

💡 Long ride with race pace practice!""",
    },
    "run": {
        "8km easy aerobic": """🏃 RUN - Easy Aerobic (55min)

WARM-UP (5min):
• Easy jog + dynamics

MAIN RUN (45min):
• 8km @ Zone 2
• Easy, conversational pace
• Cadence: 170-180 spm

COOL-DOWN:
• 5min walk + stretch

💡 Foundation run - keep it truly easy!""",
        "9km easy + strides": """🏃 RUN - Easy + Strides (60min)

WARM-UP (5min):
• Easy jog + dynamics

MAIN RUN (45min):
• 9km @ easy pace
• Zone 2

STRIDES (10min):
• 6x20s fast but smooth
  - Walk 40s between
  - Quick turnover focus

COOL-DOWN:
• Walk + stretch

💡 Build with neuromuscular work!""",
        "9km easy": """🏃 RUN - Easy (60min)

WARM-UP (5min):
• Easy jog

MAIN RUN (50min):
• 9km @ Zone 2
• Truly easy effort
• Practice good form

COOL-DOWN (5min):
• Walk + stretch

💡 Easy aerobic development.""",
        "10km easy": """🏃 RUN - Easy (65min)

WARM-UP (5min):
• Easy jog + dynamics

MAIN RUN (55min):
• 10km @ easy aerobic
• Zone 2 effort
• Comfortable breathing

COOL-DOWN (5min):
• Walk + stretch

💡 Building run volume at easy effort.""",
        "12km long run": """🏃 LONG RUN (80min)

WARM-UP (5min):
• Easy jog + dynamics

MAIN RUN (70min):
• 12km progressive
• First 9km: Zone 2 easy
• Last 3km: Moderate push

COOL-DOWN (5min):
• Walk + stretch

💡 Take a gel at 45min if needed.""",
        "13km long run": """🏃 LONG RUN (85min)

WARM-UP (5min):
• Easy jog

MAIN RUN (75min):
• 13km progressive
• 10km @ Zone 2
• Final 3km @ moderate

COOL-DOWN (5min):
• Walk + stretch + foam roll

💡 Practice race day nutrition timing!""",
        "14km long run": """🏃 LONG RUN (90min)

WARM-UP (5min):
• Easy jog

MAIN RUN (80min):
• 14km progressive
• First 11km: Easy Zone 2
• Last 3km: Moderate Zone 3

COOL-DOWN (5min):
• Walk + stretch

💡 Take gel at 45min. Hydrate throughout!""",
        "15km long run": """🏃 LONG RUN (95min)

WARM-UP (5min):
• Easy jog

MAIN RUN (85min):
• 15km progressive
• 12km @ Zone 2
• Final 3km @ stronger effort

COOL-DOWN (5min):
• Walk + stretch + foam roll

💡 Race distance practice! Test nutrition.""",
        "15km moderate": """🏃 LONG RUN MODERATE (95min)

WARM-UP (5min):
• Easy jog

MAIN RUN (85min):
• 15km @ Zone 2-3
• Slightly harder than easy
• Practice race effort

COOL-DOWN (5min):
• Walk + stretch

💡 Building race-specific fitness!""",
        "16km long run": """🏃 LONG RUN (100min)

WARM-UP (5min):
• Easy jog

MAIN RUN (90min):
• 16km progressive
• 12km @ Zone 2
• 4km @ race effort

COOL-DOWN (5min):
• Walk + stretch + foam roll

💡 Longest long run! Full race simulation.
Nutrition: Gel at 45min, 75min. Hydrate!""",
        "6km easy recovery": """🏃 RECOVERY RUN (40min)

⚡ RECOVERY WEEK

• All at Zone 1-2
• Super easy effort
• Shake out the legs
• 6km very comfortable

💡 RECOVERY - easier than you think!""",
        "7km easy": """🏃 EASY RUN (45min)

RECOVERY RUN

• 7km @ Zone 2
• Easy, conversational
• Relaxed form

💡 Recovery week - keep it easy!""",
        "9km with 25min tempo": """🏃 TEMPO RUN (60min)

WARM-UP (10min):
• 2km easy jog

TEMPO SET (25min):
• 4-5km @ Tempo pace (Zone 3-4)
  - Comfortably hard
  - Can speak in phrases
  - Hold steady!

COOL-DOWN (10min):
• 2km easy jog + stretch

💡 Tempo = race pace practice!""",
        "9km + 6x3min hills": """🏃 HILL INTERVALS (60min)

WARM-UP (10min):
• 2km easy + dynamics

HILL REPEATS:
• 6x3min uphill @ hard effort
  - Jog back down recovery
  - Stay tall, pump arms
  - Short, quick steps

COOL-DOWN (10min):
• 2km easy + stretch

💡 Hill strength = race power! Focus on form.""",
        "10km with 5x1km fast": """🏃 INTERVAL RUN (60min)

WARM-UP (15min):
• 3km easy jog + dynamics + 4 strides

INTERVALS (30min):
• 5x1km @ 10K race pace or faster
  - Rest: 90s jog between
  - Stay relaxed
  - Quick turnover

COOL-DOWN (15min):
• 2km easy + stretch

💡 Speed work for race performance!""",
        "5km easy": """🏃 EASY RUN (35min)

BRICK RUN - after bike

• 5km @ easy effort
• Zone 2
• Light and relaxed
• Let legs adapt from bike

💡 Brick = bike-to-run adaptation!""",
        "6km easy": """🏃 EASY RUN (40min)

BRICK RUN - after bike

• 6km @ Zone 2
• Conversational pace
• Recovery focus
• Let legs settle

💡 Easy brick run - bike-to-run adaptation!""",
    },
}


def get_workout_details(session_type: str, session_name: str, details: str) -> str:
    """Map CSV row to workout library and return full details."""
    stype = session_type.lower()
    if stype not in WORKOUT_LIBRARY:
        return details or session_name

    lib = WORKOUT_LIBRARY[stype]

    # Swim: extract distance - prefer "Total: XXXXm" from Notes
    if stype == "swim":
        total_m = re.search(r"Total:\s*(\d{3,4})m", details or "", re.I)
        dist = (total_m.group(1) + "m") if total_m else ""
        if not dist:
            m = re.search(r"(\d{3,4})m", details or "")
            dist = m.group(1) + "m" if m else ""
        if "Technique + Endurance" in session_name and "2100" in dist:
            return lib.get("2100m technique", details)
        if "Drill + Endurance" in session_name and "2200" in dist:
            return lib.get("2200m drill + endurance", details)
        if "CSS Test" in session_name:
            return lib.get("2400m - 400m TT + 200m TT", details)
        if "Easy Technique" in session_name and "1600" in dist:
            return lib.get("1600m easy", details)
        if "Easy Swim" in session_name and "1800" in dist:
            return lib.get("1800m easy", details)
        if "Threshold Sets" in session_name and "2700" in dist:
            return lib.get("2700m threshold", details)
        if "Threshold Pyramid" in session_name:
            return lib.get("2500m threshold pyramid", details)
        if "Race Pace Sets" in session_name:
            return lib.get("2600m race pace", details)
        if "Race Simulation" in session_name:
            return lib.get("2700m - 1900m straight", details)

    # Strength: direct match
    if stype == "strength":
        key = session_name.strip()
        if key in lib:
            return lib[key]
        if "PUSH + CORE Light" in session_name or "Light" in session_name and "PUSH" in session_name:
            return lib.get("PUSH + CORE Light", details)
        if "LEGS Light" in session_name or "LEGS light" in session_name:
            return lib.get("LEGS light", details)

    # Bike: map by session name
    if stype == "bike":
        if "ROUVY Climber" in session_name:
            return lib.get("Long endurance ROUVY", details)
        if "Long Endurance" in session_name and "Hills" not in session_name and "3+" not in (details or ""):
            return lib.get("Long endurance", details)
        if "Long Endurance + Hills" in session_name:
            return lib.get("Long + hills", details)
        if "3+ hour" in (details or "") or "3h+" in (details or ""):
            return lib.get("3h+ long ride", details)
        if "Easy ROUVY" in session_name:
            return lib.get("Easy ROUVY", details)
        if "ROUVY + Hills" in session_name:
            return lib.get("ROUVY + hills + PULL", details)
        if "Easy Endurance + Brick" in session_name or "Easy + Brick" in session_name:
            return lib.get("Easy endurance", details)
        if "Sweet Spot" in session_name:
            return lib.get("3x12min @ SS + PULL", details)
        if "Hill Repeats" in session_name:
            return lib.get("6x5min @ 90% FTP + PULL", details)
        if "Long Ride with Climbs" in session_name or "Grizzlyman" in (details or ""):
            return lib.get("Long with climbs", details)
        if "Threshold Blocks" in session_name:
            return lib.get("2x20min @ FTP + PULL", details)
        if "Long + Race Pace" in session_name:
            return lib.get("Long + race pace", details)
        if "Easy Endurance" in session_name:
            return lib.get("Easy endurance", details)

    # Run: extract distance from Details
    if stype == "run":
        m = re.search(r"(\d+)km", details or session_name or "")
        km = m.group(1) if m else ""
        if "Easy Aerobic" in session_name and km == "8":
            return lib.get("8km easy aerobic", details)
        if "Easy + Strides" in session_name and km == "9":
            return lib.get("9km easy + strides", details)
        if "Easy Aerobic" in session_name and km == "9":
            return lib.get("9km easy", details)
        if "Easy Aerobic" in session_name and km == "10":
            return lib.get("10km easy", details)
        if "Long Run" in session_name and km == "12":
            return lib.get("12km long run", details)
        if "Long Run" in session_name and km == "13":
            return lib.get("13km long run", details)
        if "Long Run" in session_name and km == "14":
            return lib.get("14km long run", details)
        if "Long Run" in session_name and km == "15" and "moderate" not in (details or "").lower():
            return lib.get("15km long run", details)
        if "Long Run" in session_name and "15km moderate" in (details or ""):
            return lib.get("15km moderate", details)
        if "Long Run" in session_name and km == "16":
            return lib.get("16km long run", details)
        if "Easy Recovery" in session_name and km == "6":
            return lib.get("6km easy recovery", details)
        if "Easy Recovery" in session_name and km == "7":
            return lib.get("7km easy", details)
        if "Tempo Run" in session_name:
            return lib.get("9km with 25min tempo", details)
        if "Hill Intervals" in session_name:
            return lib.get("9km + 6x3min hills", details)
        if "Interval Run" in session_name:
            return lib.get("10km with 5x1km fast", details)
        if "Easy Brick" in session_name and km == "5":
            return lib.get("5km easy", details)
        if "Easy Brick" in session_name and km == "6":
            return lib.get("6km easy", details)

    return details or session_name


def parse_time(time_str: str, date_str: str) -> tuple:
    """Parse time string to (hour, minute). Default 06:00 for morning."""
    if not time_str or time_str.upper() == "REST":
        return (6, 0)
    m = re.match(r"(\d{1,2}):(\d{2})", str(time_str))
    if m:
        return (int(m.group(1)), int(m.group(2)))
    return (6, 0)


def escape_ics(text: str) -> str:
    """Escape text for ICS format."""
    if not text:
        return ""
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def generate_ics(weekly_dir: Path, output_path: Path, months: list[str]) -> None:
    """Generate ICS file from CSV files."""
    events = []
    last_bike_end = None
    last_date = None

    # Weeks 6-14 = Feb 2 - Apr 5 (we filter by month)
    week_files = sorted(weekly_dir.glob("week_*.csv"))
    week_files = [f for f in week_files if any(f.name.startswith(f"week_{i:02d}") for i in range(6, 15))]

    for week_file in week_files:
        with open(week_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row:
                    continue
                session_type = (row.get("Session_Type") or "").strip()
                if session_type not in ("Swim", "Bike", "Run", "Strength"):
                    continue
                if "Morning Espresso" in row.get("Session_Name", "") or "Mobility" in session_type:
                    continue

                date_str = row.get("Date", "")
                if not date_str or not re.match(r"\d{4}-\d{2}-\d{2}", date_str):
                    continue

                year, month, day = date_str.split("-")
                if month not in months:
                    continue

                # Reset "after bike" when date changes
                if date_str != last_date:
                    last_bike_end = None
                    last_date = date_str

                time_str = row.get("Time", "06:00")
                duration = int(row.get("Duration", 0) or 0)

                if "after bike" in str(time_str or "").lower():
                    if last_bike_end:
                        # Small transition gap
                        start_dt = last_bike_end + timedelta(minutes=5)
                    else:
                        start_dt = datetime(int(year), int(month), int(day), 6, 0)
                else:
                    h, m = parse_time(time_str, date_str)
                    start_dt = datetime(int(year), int(month), int(day), h, m)

                end_dt = start_dt + timedelta(minutes=duration) if duration else start_dt + timedelta(minutes=45)

                if session_type == "Bike":
                    last_bike_end = end_dt
                else:
                    last_bike_end = None

                session_name = row.get("Session_Name", "")
                details = row.get("Details", "")
                notes_col = row.get("Notes", "")
                details_for_lookup = f"{details or ''} {notes_col or ''}"
                notes = get_workout_details(session_type, session_name, details_for_lookup)

                emoji = EMOJI.get(session_type, "")
                summary = f"{emoji} {session_type} - {session_name}"
                if len(summary) > 80:
                    summary = f"{emoji} {session_type} - {session_name[:60]}..."

                desc = escape_ics(notes)
                loc = LOCATION.get(session_type, "")

                dt_start = start_dt.strftime("%Y%m%dT%H%M00")
                dt_end = end_dt.strftime("%Y%m%dT%H%M00")
                uid = f"{date_str.replace('-', '')}-{session_type.lower()}-{abs(hash(week_file.name + row.get('Day', '') + time_str)) % 100000}@training2026"

                events.append((dt_start, dt_end, summary, desc, loc, uid))

    # Write ICS
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("BEGIN:VCALENDAR\r\n")
        f.write("VERSION:2.0\r\n")
        f.write("PRODID:-//Training Plan 2026//Half Ironman Feb-Mar//EN\r\n")
        f.write("CALSCALE:GREGORIAN\r\n")
        f.write("METHOD:PUBLISH\r\n")
        f.write("X-WR-CALNAME:Training Plan 2026 Feb-Mar\r\n")
        f.write("X-WR-TIMEZONE:Europe/Prague\r\n")

        for dt_start, dt_end, summary, desc, loc, uid in events:
            f.write("BEGIN:VEVENT\r\n")
            f.write(f"DTSTART:{dt_start}\r\n")
            f.write(f"DTEND:{dt_end}\r\n")
            f.write(f"SUMMARY:{escape_ics(summary)}\r\n")
            if desc:
                f.write(f"DESCRIPTION:{desc}\r\n")
            if loc:
                f.write(f"LOCATION:{escape_ics(loc)}\r\n")
            f.write(f"UID:{uid}\r\n")
            f.write("END:VEVENT\r\n")

        f.write("END:VCALENDAR\r\n")

    print(f"Generated {len(events)} events -> {output_path}")


def main():
    script_dir = Path(__file__).parent
    weekly_dir = script_dir / "weekly"
    output_path = script_dir / "training_calendar_2026_feb_mar.ics"

    if not weekly_dir.exists():
        print(f"Error: {weekly_dir} not found")
        return 1

    generate_ics(weekly_dir, output_path, months=["02", "03"])
    return 0


if __name__ == "__main__":
    exit(main())
