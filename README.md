# Check USCIS case status

If you are applying for a :us:US visa you might find yourself constantly checking the USCIS website for updates - which can be quite nerve-wracking.
I searched for USCIS scrapers that could automatically notify me of any changes, but the ones I came across were outdated and no longer functional (at least didn’t work for me). I decided to give it a try with Selenium, GitHub Actions and SendGrid and ended up with a script that checks my status and sends me an email if anything changes (and writes in a .csv file the status every time it runs - not really sure how that would be useful but I wanted to keep a log it). On current settings it runs once every hour.

Main script is `check_status.py`. It uses Selenium to check on the USCIS website, look for the case number and identify case status and description.
It reads the last entry in the `status_check.csv` file. If the case status has changed, it sends an email notifying about the change.
Every time it runs it writes the data to a `status_check.csv` file.

Remember to replace the following variables with the correct information inside GitHub Secrets.

* CASE_NUMBER: your USCIS case number
* FROM_EMAIL: the email you are sending from (must be authenticated on SendGrid)
* TO_EMAIL: the email you are sending to
* SENDGRID_API_KEY: your SendGrid API Key. For more info on how to send emails from Python with SendGrid there's [this short and easy video](https://www.youtube.com/watch?v=xCCYmOeubRE).

**Marco Dalla Stella**
[md3934@columbia.edu](mailto:md3934@columbia.edu)
