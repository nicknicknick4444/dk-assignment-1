# IMPORT MODULES
import requests, json, csv, datetime, sys, smtplib, time
import pandas as pd
import numpy as np

### OUR MAIN VARIABLES ###
url = "https://raw.githubusercontent.com/dk-books/tech-interview/refs/heads/main/ae/books.json"
chosen_cats = ["Nonfiction", "Hobbies"]

# CREATE TIMESTAMP FOR FIILENAME
now = datetime.datetime.now()
timestamp_filename = str(now.strftime("%d-%m-%Y_%H_%M_%S"))
timestamp_log = str(now.strftime("on %d/%m/%Y at %H:%M:%S"))

# MAIN API CALL FOR RAW JSON DATA
data = requests.get(url).json()

### DEFINE HELPER FUNCTIONS ###
# Checks categories within each category list (B00OLEAN OUTPUT; True or loop continues):
def cat_checker(this_cat):
    for i in this_cat:
# returns True as soon as the provided 'arg' is found in 'chosen_cats':
        if i in chosen_cats:
#             Enable this print statement below to check the output  
#             print(i)
            return i

# Checks if 'publication_date' is after the user's specified year (B00OLEAN OUTPUT): 
def after_year_check(pub_date):
#     Returns True if the date is later than 2020
    limit = time.strptime("2020-12-31", "%Y-%m-%d")
    return time.strptime(pub_date, "%Y-%m-%d") > limit

# .txt log-writer:
def write_log(err_type, message):
    with open("Logs/" + err_type + "_log.txt", "a") as f:
        f.write(message)

# # # MAIN FUNCTION # # #
def main():
# # # DATA-WRANGLING SECTION # # #
#     Make JSON into Pandas dataframe
    print("Starting program...")
    orig_data = pd.DataFrame(pd.json_normalize(data))

#     Filter within each line's 'categories' list struture for the required categories, \
#     as defined in 'chosen_cats' earlier:
    filt_data = orig_data[orig_data["categories"].apply(lambda x: cat_checker(x)).isin(chosen_cats)]

#     Add 20% to prices if book's publication_date is later than 2020: 
    filt_data2 = filt_data.copy() # <-- Note: Making this copy prevents unsightly "copy of a slice" warning
    filt_data2["price"] = np.where(filt_data2["publication_date"].apply(lambda x: after_year_check(x)), \
                                   round(filt_data2["price"] * 1.2, 2), filt_data2["price"].apply(lambda x: "%.2f" % x))

#     Enable these print statements to check the outputs during testing:
#     print(filt_data2["publication_date"].apply(lambda x: after_year_check(x, 2020)))
#     print(filt_data2["price"])

#     Write to CSV
    print(f"Writing dk_book_data_{timestamp_filename}.csv to Output folder")
    filt_data2.to_csv(f"Output/dk_book_data_{timestamp_filename}.csv", index = False)

# ALL DONE!

### RUN MAIN FUNCTION, BUT BE READY TO CATCH ERRORS ###
if __name__ == "__main__":
    try:
#         Success:
        main()
#         Log success to file; handy if running on a cron
        write_log("success", f"Ran {timestamp_log} successfully\n")
        print("completed successfully!")
    except Exception as e:
#         Faliure: 
        print("--AN ERROR HAS OCCURRED!--\nERROR TYPE:", type(e).__name__, "\nMESSAGE:", e, file=sys.stderr)
        err_msg = f"{type(e).__name__} {timestamp_log}: {e}\n"
#         Record error to error log. But that's not all...
        write_log("error", err_msg)
#         ...Email the IT guy about the error! NOTE: Without an email server, this only appears to only succeed with \
#         work/ domain email addresses like the below, and not with Hotmail or Gmail etc 
        email_server = smtplib.SMTP("nickhartprojects.co.uk", 25)
        email_server.ehlo()
        email_server.starttls()
        email_server.sendmail("errors@demo.com", "nick@nickhartprojects.co.uk", \
                              "Subject: ERROR NOTIFICATION: " + f"{type(e).__name__}"  + "\n\n" + err_msg)
        email_server.quit()
        exit()

### END ### 