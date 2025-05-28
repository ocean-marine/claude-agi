
⸻

Guide to Using the date Command

Basic Syntax

date [OPTIONS] [+FORMAT]

Common Usage

# Display the current date and time
date

# Show time in UTC
date -u

# Display with a custom format
date +%Y-%m-%d

Major Options
	•	-d STRING : Display the date described by STRING.
	•	-r FILE   : Show the last modification time of FILE.
	•	-u        : Display UTC time.

Frequently Used Format Specifiers
	•	%Y : 4-digit year (e.g., 2025)
	•	%m : Month (01–12)
	•	%d : Day of month (01–31)
	•	%H : Hour (00–23)
	•	%M : Minute (00–59)
	•	%S : Second (00–59)
	•	%F : ISO 8601 date (%Y-%m-%d)
	•	%T : Time (%H:%M:%S)

Practical Examples

# YYYY-MM-DD format
date +%Y-%m-%d

# Date and time together
date '+%Y-%m-%d %H:%M:%S'

# Tomorrow’s date
date -d "tomorrow" +%Y-%m-%d

# One week ago
date -d "1 week ago" +%Y-%m-%d

# Show a file’s last modification time
date -r /etc/passwd