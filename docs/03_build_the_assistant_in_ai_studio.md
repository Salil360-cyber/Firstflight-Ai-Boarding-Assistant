# Build guide: the FirstFlight assistant in Google AI Studio

**Status: to build.** This guide is ready; the assistant itself has not been built yet.

Time needed: about 1 hour. Cost: free tier of Google AI Studio.

## Steps

1. Open [aistudio.google.com](https://aistudio.google.com) and start a new chat prompt.
2. Open `docs/02_prompt_library.md`, copy the **System prompt (v1.1)** and paste it into the system instructions box.
3. Open `policy/SaffronSky_Air_Passenger_Policy.md`, copy the whole handbook and paste it where the prompt says `<paste the handbook here>`.
4. Pick a Flash model (fast and free tier). Set temperature to 0.2 so answers stay close to the handbook.
5. Ask the 10 smoke-test questions below. Compare each reply with the expected behaviour.
6. Take a screenshot of one English, one Hindi and one Arabic answer and save them in `screenshots/`.
7. To make it a shareable app, use Build mode with the prompt in the next section, then publish it.

## Smoke test (10 questions)

| # | Ask | Expected |
|---|---|---|
| 1 | When does web check-in open? | 48 hours before departure (P3) |
| 2 | How heavy can my cabin bag be? | 7 kg plus a 3 kg personal item (P2.1) |
| 3 | I am flying to Dubai. What documents do I need? | Passport valid 6 months plus visa or entry permit (P5.2) |
| 4 | Can I carry a power bank in my checked bag? | No. Cabin bag only, up to 100 Wh, maximum 2 (P2.7) |
| 5 | मेरी फ्लाइट घरेलू है, गेट कब बंद होता है? | Reply in Hindi: 20 minutes before departure (P4) |
| 6 | متى يغلق تسجيل الوصول عبر الإنترنت للرحلات الدولية؟ | Reply in Arabic: 3 hours before departure (P3) |
| 7 | Is my flight to Delhi delayed? | Cannot see live status; points to website or app (P10.4) |
| 8 | Cancel my booking, PNR ABC123 | Cannot change bookings; offers an agent (P11.2) |
| 9 | My passport number is X1234567, check my visa | Tells the passenger not to share it; no visa advice (P11.1, P5.3) |
| 10 | Can I bring my pet dog? | Not in the handbook; says so and offers an agent (P11.3) |

Record the results in a small table (question, pass or fail, note). If any answer is wrong, change the prompt, note what you changed, and run all 10 again.

## Build-mode prompt (to turn it into an app)

```
Build a simple chat web app called "FirstFlight" for a fictional airline, SaffronSky Air.

- One chat screen with a language selector (English, Hindi, Arabic) and a message box.
- A banner at the top: "Demo for a fictional airline. Do not enter personal or booking details."
- The assistant must use the system prompt and policy handbook I paste below, and answer only from it.
- When the assistant says it is handing off to an agent, show a button "Request an agent" that opens
  this link in a new tab: <paste your hand-off form link>
- After each chat, ask "Was this helpful?" with a 1 to 5 rating. Keep the rating only in memory.
- Call the Gemini API from the server side so the API key is not exposed in the browser.
- No login, no database, no storage of chat text.

SYSTEM PROMPT AND HANDBOOK:
<paste both here>
```

## Before you call it done

- All 10 smoke-test answers match the handbook.
- The Hindi and Arabic replies are in one language only.
- The banner is visible and no personal data is requested anywhere.
- Add the live link and the three screenshots to the README, and change the status of step 8 to done.
