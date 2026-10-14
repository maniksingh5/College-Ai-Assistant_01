import os
import math
from dotenv import load_dotenv
from google import genai

# Load Gemini API key from .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL = "gemini-flash-latest"

client = genai.Client(api_key=API_KEY) if API_KEY else None


def line():
    print("-" * 50)


def get_number(prompt, minimum=None, maximum=None):
    while True:
        try:
            value = float(input(prompt))

            if not math.isfinite(value):
                raise ValueError

            if minimum is not None and value < minimum:
                print(f"Value must be at least {minimum}.")
                continue

            if maximum is not None and value > maximum:
                print(f"Value must not exceed {maximum}.")
                continue

            return value

        except ValueError:
            print("Enter a valid number.")


# 1. Attendance Calculator
def attendance_calculator():
    line()
    print("ATTENDANCE CALCULATOR")
    line()

    attended = get_number("Classes attended: ", 0)
    total = get_number("Total classes held: ", 0)

    if attended > total:
        print("Attended classes cannot exceed total classes.")
        return

    target = get_number("Target attendance % (default 75): ", 0, 100)

    if target == 0:
        print("Target must be greater than zero.")
        return

    if total == 0:
        print("No classes have been held yet.")
        return

    percentage = attended / total * 100
    print(f"\nCurrent attendance: {percentage:.2f}%")

    if percentage >= target:
        if target == 100:
            print("To maintain 100%, attend every future class.")
        else:
            max_misses = math.floor(
                attended / (target / 100) - total + 1e-9
            )
            print(f"Maximum additional classes you can miss: "
                  f"{max(0, max_misses)}")
    else:
        if target == 100:
            print("Attend every future class to approach 100%.")
        else:
            needed = math.ceil(
                (target * total - 100 * attended)
                / (100 - target) - 1e-9
            )
            print(f"Consecutive classes to attend: {max(0, needed)}")
            print("Assuming you attend every future class.")


# 2. Marks Calculator
def marks_calculator():
    line()
    print("MARKS CALCULATOR")
    line()

    count = int(get_number("Number of subjects: ", 1, 100))
    subjects = []

    for i in range(count):
        print(f"\nSubject {i + 1}")
        name = input("Subject name: ").strip() or f"Subject {i + 1}"
        maximum = get_number("Maximum marks: ", 0.000001)
        obtained = get_number("Marks obtained: ", 0, maximum)

        subjects.append((name, obtained, maximum))

    total_obtained = sum(s[1] for s in subjects)
    total_maximum = sum(s[2] for s in subjects)
    percentage = total_obtained / total_maximum * 100

    print("\nSUBJECT RESULTS")
    line()

    for name, obtained, maximum in subjects:
        print(f"{name}: {obtained:g}/{maximum:g} "
              f"({obtained / maximum * 100:.2f}%)")

    line()
    print(f"Total marks: {total_obtained:g}/{total_maximum:g}")
    print(f"Overall percentage: {percentage:.2f}%")

    target = get_number("Target percentage (0 to skip): ", 0, 100)

    if target > 0:
        required = target / 100 * total_maximum - total_obtained

        if required <= 0:
            print("You have already achieved your target.")
        elif required <= total_maximum - total_obtained:
            print(f"Additional marks needed across this total: "
                  f"{required:.2f}")
        else:
            print("Target is not possible within the current maximum.")

    print("CGPA depends on your college's grading rules.")


# 3. Timetable Analyzer
def timetable_analyzer():
    line()
    print("TIMETABLE ANALYZER")
    line()
    print("Enter: Monday | 09:00-10:00 | Mathematics")
    print("Press Enter on an empty line to finish.\n")

    entries = {}

    while True:
        row = input().strip()

        if not row:
            break

        try:
            parts = [p.strip() for p in row.split("|")]

            if len(parts) != 3:
                raise ValueError("Use Day | HH:MM-HH:MM | Subject")

            day, time_range, subject = parts
            times = time_range.split("-")

            if len(times) != 2 or not day or not subject:
                raise ValueError("Invalid timetable entry.")

            start, end = times[0].strip(), times[1].strip()

            def to_minutes(value):
                h, m = map(int, value.split(":"))
                if not (0 <= h <= 23 and 0 <= m <= 59):
                    raise ValueError("Invalid time.")
                return h * 60 + m

            start_min = to_minutes(start)
            end_min = to_minutes(end)

            if end_min <= start_min:
                raise ValueError("End time must be after start time.")

            key = day.lower()
            entries.setdefault(key, {"day": day, "classes": []})
            entries[key]["classes"].append(
                (start_min, end_min, start, end, subject)
            )

        except ValueError as error:
            print(f"Invalid entry: {error}")
            continue

    if not entries:
        print("No valid timetable entries.")
        return

    total_classes = 0
    schedule = []

    for group in entries.values():
        classes = sorted(group["classes"])

        for i in range(1, len(classes)):
            if classes[i][0] < classes[i - 1][1]:
                print(f"Overlapping classes on {group['day']}.")
                print("Please correct the timetable and try again.")
                return

        total_classes += len(classes)
        schedule.append((group["day"], classes))

    print(f"\nTotal classes: {total_classes}")

    for day, classes in schedule:
        print(f"\n{day} — {len(classes)} classes")

        for _, _, start, end, subject in classes:
            print(f"  {start}-{end}: {subject}")

        for i in range(1, len(classes)):
            previous = classes[i - 1]
            current = classes[i]
            gap = current[0] - previous[1]

            if gap > 0:
                print(f"  Free period: {gap} minutes "
                      f"between {previous[4]} and {current[4]}")

    # Optional AI analysis
    prompt = (
        "Analyze this college timetable. Summarize daily workload, "
        "free periods and study-planning suggestions. Do not invent "
        "class timings.\n" + repr(schedule)
    )
    ask_gemini(prompt)


# 4. Gemini AI Chatbot
def ask_gemini(prompt):
    if not client:
        print("\nGemini API key missing. Configure your .env file.")
        return

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        print("\nGemini AI:")
        line()
        print(response.text or "No response received.")
        line()

    except Exception as error:
        print("\nGemini request failed.")
        print("Check internet, API key, model access and API quota.")
        print(f"Details: {error}")


def chatbot():
    line()
    print("COLLEGE AI CHATBOT")
    print("Type 'back' to return to the main menu.")

    while True:
        question = input("\nYou: ").strip()

        if question.lower() == "back":
            break

        if question:
            ask_gemini(
                "You are a helpful college AI assistant. Help with "
                "engineering subjects, exams, study planning, college "
                "life, attendance and marks. Do not invent official rules.\n"
                + question
            )


# Main Menu
def main():
    print("\n===================================")
    print("      COLLEGE AI ASSISTANT")
    print("===================================")

    if not client:
        print("Gemini key not configured. Local calculators still work.")

    while True:
        print("\n1. Attendance Calculator")
        print("2. Marks Calculator")
        print("3. Timetable Analysis")
        print("4. Gemini AI Chatbot")
        print("5. Exit")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            attendance_calculator()
        elif choice == "2":
            marks_calculator()
        elif choice == "3":
            timetable_analyzer()
        elif choice == "4":
            chatbot()
        elif choice == "5":
            print("Exiting College AI Assistant.")
            break
        else:
            print("Invalid option. Choose 1-5.")


if __name__ == "__main__":
    main()