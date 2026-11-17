import os
import json
from datetime import datetime, timedelta
from garminconnect import Garmin

def main():
    email = os.environ.get("GARMIN_EMAIL")
    password = os.environ.get("GARMIN_PASSWORD")

    client = Garmin(email, password)
    client.login()

    today = datetime.now().date()
    week_ago = today - timedelta(days=7)

    activities = client.get_activities_by_date(week_ago.isoformat(), today.isoformat())

    total_km = 0.0
    run_count = 0
    workout_count = 0
    recent_list = []

    for act in activities:
        act_type = act.get("activityType", {}).get("typeKey", "")
        name = act.get("activityName", "Training")
        date_str = act.get("startTimeLocal", "")[:10]
        dist_m = act.get("distance") or 0
        dur_s = act.get("duration") or 0
        avg_hr = act.get("averageHR") or 0

        dist_km = round(dist_m / 1000, 2)
        pace_str = "-"

        if "running" in act_type or "run" in act_type:
            run_count += 1
            total_km += dist_km
            if dist_km > 0 and dur_s > 0:
                pace_sec = dur_s / dist_km
                mins = int(pace_sec // 60)
                secs = int(pace_sec % 60)
                pace_str = f"{mins}:{secs:02d}/km"
        else:
            workout_count += 1

        recent_list.append({
            "date": date_str,
            "name": name,
            "km": dist_km,
            "pace": pace_str,
            "hr": int(avg_hr) if avg_hr else "-"
        })

    output = {
        "last_updated": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "total_km": round(total_km, 1),
        "run_count": run_count,
        "workout_count": workout_count,
        "activities": recent_list[:6]
    }

    with open("garmin_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
