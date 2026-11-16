# Build guide: hand-off automation (form → Excel log → agent email)

**Status: to build.** The Excel log template is ready in `templates/handoff_log_template.xlsx`. The flow itself has not been built yet.

What it does: when the assistant cannot help, the passenger fills a short form. Each response is added as a row to an Excel log and an email goes to the agent inbox.

You need a Microsoft account with Forms, Excel Online and Power Automate. Menu names in Power Automate change from time to time, so if a name below is slightly different, search for the closest match.

## 1. Create the form (Microsoft Forms)

Title: **FirstFlight: request an agent**

| # | Question | Type | Choices |
|---|---|---|---|
| 1 | Your email | Text | |
| 2 | Language | Choice | English, Hindi, Arabic |
| 3 | Topic | Choice | Check-in, Baggage, Boarding, ID and documents, Refunds and changes, Special assistance, Add-ons, Delays, Name change, Other |
| 4 | Why do you need an agent? | Choice | About my booking, Live flight status, The assistant did not know, I prefer a person |
| 5 | Your question | Long text | |

Add this line under the title: "Do not enter passport, Aadhaar or card numbers."

## 2. Put the Excel log online

1. Upload `templates/handoff_log_template.xlsx` to OneDrive.
2. Open it in Excel Online. The sheet **Log** already has a table named **HandoffLog** with these columns: `logged_at`, `email`, `language`, `topic`, `reason`, `question`, `status`.

## 3. Build the flow (Power Automate)

1. Create → **Automated cloud flow**. Name it `FirstFlight hand-off`.
2. Trigger: **Microsoft Forms – When a new response is submitted**. Pick your form.
3. Add action: **Microsoft Forms – Get response details**. Form: your form. Response Id: the value from the trigger.
4. Add action: **Excel Online – Add a row into a table**. Pick the file and the table `HandoffLog`. Map the fields:

| Column | Value |
|---|---|
| logged_at | `utcNow()` (expression) |
| email | Your email |
| language | Language |
| topic | Topic |
| reason | Why do you need an agent? |
| question | Your question |
| status | `New` |

5. Add action: **Outlook – Send an email (V2)**.
   - To: your own address (acting as the agent inbox)
   - Subject: `FirstFlight hand-off: ` + Topic + ` (` + Language + `)`
   - Body: Reason, Question and the passenger's email, each on its own line
6. Save, then click **Test → Manually** and submit the form once.

## 4. Check it works

| Check | Expected |
|---|---|
| Submit the form | Flow run shows "Succeeded" |
| Excel log | One new row with status `New` |
| Email | One email with the topic and language in the subject |
| Submit 3 more with different topics | 4 rows in total, 4 emails |

## 5. What to save in this repo

- A screenshot of the flow (all four steps visible) → `screenshots/power_automate_flow.png`
- A screenshot of the Excel log with your 4 test rows → `screenshots/handoff_log.png`
- Then change the status of step 9 in the README to done.

## How to explain it in an interview

"When the assistant cannot answer, the passenger fills a five-question form. Power Automate picks up each response, writes it to an Excel log so nothing is lost, and emails the agent with the topic and language in the subject, so the agent does not have to ask the passenger to repeat everything."
