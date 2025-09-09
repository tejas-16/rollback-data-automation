#!/usr/bin/env python3
import csv
import os

file_path = "rollback_data.csv"
headers = ["Application_and_Area", "Rollback_Ticket", "Rollback_Reason", "Incident_Ticket", "Rollback_Date", "Business_impact"]

# Read inputs from environment variables
Application_and_Area = os.environ.get("App_Area", "N/A")
Rollback_Ticket = os.environ.get("Ticket", "N/A")
Rollback_Reason = os.environ.get("Reason", "N/A")
Incident_Ticket = os.environ.get("Incident", "N/A")
Rollback_Date = os.environ.get("Date", "N/A")
Business_impact = os.environ.get("Impact", "N/A")

row = [Application_and_Area, Rollback_Ticket, Rollback_Reason, Incident_Ticket, Rollback_Date, Business_impact]

file_exists = os.path.isfile(file_path)

with open(file_path, "a", newline="") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(headers)
    writer.writerow(row)

print("Added rollback entry: {}".format(row))
