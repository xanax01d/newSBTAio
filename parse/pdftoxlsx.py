import PyPDF2
import re


def parse_pdf_schedule(path):
    with open(path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        schedule_data = []

        for page in reader.pages:
            text = page.extract_text()
            #print(text)
            if text:
                lines = text.split('\n')
                days_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
                current_day = None

                for line in lines:
                    for day in days_of_week:
                        if day in line:
                            current_day = day
                            break

                    # Use regex to find groups, times, and schedules
                    matches = re.findall(r'(\d+)\s+([\d:.-]+)\s+([\w\s,()]+)', line)
                    for match in matches:
                        group, time, schedule = match
                        schedule_data.append(f"{group.strip()} - {current_day} - {time.strip()} - {schedule.strip()}")

    return schedule_data


# Path to your PDF file
path = 'Curs3-11.pdf'  # Update with the correct path if necessary

# Parse the PDF and print results
parsed_schedule = parse_pdf_schedule(path)
for entry in parsed_schedule:
    print(entry)
