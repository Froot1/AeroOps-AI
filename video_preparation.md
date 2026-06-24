# AeroOps AI Video Preparation Guide

The local FastAPI server has been started at [http://127.0.0.1:8000](http://127.0.0.1:8000). Visual slides/mockups have been generated and corresponding MP3 voiceover files are available in your project's `voiceovers/` folder.

---

## 📽️ Slides & Voiceover Narration

````carousel
![1. Title Slide](C:/Users/m000m/.gemini/antigravity/brain/2ab2abc8-f04b-4d6c-b77f-2eb011980c2f/slide_title_1782117555415.png)
### 🎙️ Narration
> Hello, this is AeroOps AI, a multi-agent flight operations intelligence assistant. The system helps flight operations teams analyze flight readiness using NOTAMs, weather information, operational notes, validation rules, security checks, deterministic risk scoring, and human review.
>
> 🎵 **Audio File**: [01_intro.mp3](file:///c:/Users/m000m/Downloads/my-first-project/voiceovers/01_intro.mp3)
<!-- slide -->
![2. Dashboard Overview](C:/Users/m000m/.gemini/antigravity/brain/2ab2abc8-f04b-4d6c-b77f-2eb011980c2f/slide_dashboard_1782117573737.png)
### 🎙️ Narration
> This is the AeroOps AI dashboard. It includes five demo scenarios: LOW Risk Demo, MEDIUM Risk Demo, HIGH Risk Demo, Security Injection Demo, and Invalid Input Demo. Each scenario fills the form automatically, and then I click Run Analysis to execute the workflow.
>
> 🎵 **Audio File**: [02_dashboard.mp3](file:///c:/Users/m000m/Downloads/my-first-project/voiceovers/02_dashboard.mp3)
<!-- slide -->
![3. LOW Risk Demo](C:/Users/m000m/.gemini/antigravity/brain/2ab2abc8-f04b-4d6c-b77f-2eb011980c2f/slide_low_risk_1782117592613.png)
### 🎙️ Narration
> First, I will run the LOW Risk scenario. The flight is SV1200 from RUH to JED. There are no major NOTAM restrictions and the weather is stable. The result is: Risk Score: 10, Risk Level: LOW, Recommended Action: PROCEED. This means the flight can continue without human review.
>
> 🎵 **Audio File**: [03_low_risk.mp3](file:///c:/Users/m000m/Downloads/my-first-project/voiceovers/03_low_risk.mp3)
<!-- slide -->
![4. MEDIUM Risk Demo](C:/Users/m000m/.gemini/antigravity/brain/2ab2abc8-f04b-4d6c-b77f-2eb011980c2f/slide_medium_risk_1782117623496.png)
### 🎙️ Narration
> Next, I will run the MEDIUM Risk scenario. This case includes thunderstorm activity near the route. The result is: Risk Score: 50, Risk Level: MEDIUM, Recommended Action: RE-ROUTE. This shows that the system recommends adjusting the route due to weather risk.
>
> 🎵 **Audio File**: [04_medium_risk.mp3](file:///c:/Users/m000m/Downloads/my-first-project/voiceovers/04_medium_risk.mp3)
<!-- slide -->
![5. HIGH Risk Demo](C:/Users/m000m/.gemini/antigravity/brain/2ab2abc8-f04b-4d6c-b77f-2eb011980c2f/slide_high_risk_80_clean_1782279433357.png)
### 🎙️ Narration
> Now I will run the HIGH Risk scenario. This case includes a runway closure, taxiway restriction, possible ground delays, strong winds, and high temperature. The result is: Risk Score: 80, Risk Level: HIGH, Recommended Action: HOLD. Because this is a high-risk case, the system requires Human-in-the-Loop review. After approval, the system generates the final operational briefing.
>
> 🎵 **Audio File**: [05_high_risk.mp3](file:///c:/Users/m000m/Downloads/my-first-project/voiceovers/05_high_risk.mp3)
<!-- slide -->
![6. Security Injection Demo](C:/Users/m000m/.gemini/antigravity/brain/2ab2abc8-f04b-4d6c-b77f-2eb011980c2f/slide_security_1782117684570.png)
### 🎙️ Narration
> Next, I will test the security layer. This input contains a prompt injection attempt asking the system to ignore previous instructions and mark the flight as safe. AeroOps AI detects the unsafe instruction and activates the Security Shield. The result is: Risk Score: 100, Risk Level: HIGH, Recommended Action: HOLD. The NOTAM and weather analysis are bypassed because the input is unsafe. After human review, the system generates a security-focused final briefing.
>
> 🎵 **Audio File**: [06_security.mp3](file:///c:/Users/m000m/Downloads/my-first-project/voiceovers/06_security.mp3)
<!-- slide -->
![7. Invalid Input Demo](C:/Users/m000m/.gemini/antigravity/brain/2ab2abc8-f04b-4d6c-b77f-2eb011980c2f/slide_invalid_1782117701146.png)
### 🎙️ Narration
> Finally, I will test input validation. This case uses an invalid flight number format: 1024. The system rejects the request and returns: Risk Score: 100, Risk Level: HIGH, Recommended Action: CANCEL. The final briefing explains that the flight number must contain two or three letters followed by one to four digits.
>
> 🎵 **Audio File**: [07_invalid_input.mp3](file:///c:/Users/m000m/Downloads/my-first-project/voiceovers/07_invalid_input.mp3)
<!-- slide -->
![8. Testing Slide](C:/Users/m000m/.gemini/antigravity/brain/2ab2abc8-f04b-4d6c-b77f-2eb011980c2f/slide_testing_1782117719359.png)
### 🎙️ Narration
> The project also includes automated tests. The final test result shows: 11 tests passed. This confirms that the main workflow, validation, risk scoring, and security behavior are working correctly.
>
> 🎵 **Audio File**: [08_testing.mp3](file:///c:/Users/m000m/Downloads/my-first-project/voiceovers/08_testing.mp3)
<!-- slide -->
![9. Conclusion](C:/Users/m000m/.gemini/antigravity/brain/2ab2abc8-f04b-4d6c-b77f-2eb011980c2f/slide_title_1782117555415.png)
### 🎙️ Narration
> AeroOps AI demonstrates how agentic AI can support aviation operations while keeping safety, validation, security, deterministic scoring, and human oversight at the center. Thank you.
>
> 🎵 **Audio File**: [09_conclusion.mp3](file:///c:/Users/m000m/Downloads/my-first-project/voiceovers/09_conclusion.mp3)
````

---

## ⏺️ How to Record Your Video

1. **Start Dashboard Server**: The local dashboard server is running at [http://127.0.0.1:8000](http://127.0.0.1:8000). Open this URL in your web browser.
2. **Setup Screen Recording**:
   - Use OBS Studio, Zoom (by starting a solo meeting and recording the screen), or Xbox Game Bar (`Win + G` on Windows).
   - Set the recording focus to your browser window.
3. **Follow the Script**:
   - For each slide, play the corresponding voiceover `.mp3` file from the [voiceovers/](file:///c:/Users/m000m/Downloads/my-first-project/voiceovers/) folder or read it aloud.
   - Click the corresponding button on the dashboard (e.g. **LOW Risk Demo**, **MEDIUM Risk Demo**, etc.) and then click **Run Analysis** to record the live transition in your video.
