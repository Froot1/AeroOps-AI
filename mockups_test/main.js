// JavaScript for AeroOps AI Mockup Walkthrough
document.addEventListener('DOMContentLoaded', () => {
    // Views
    const viewTitle = document.getElementById('view-title');
    const viewDashboard = document.getElementById('view-dashboard');
    const viewDetail = document.getElementById('view-detail');

    // Buttons
    const btnEnter = document.getElementById('btn-enter');
    const btnBackTitle = document.getElementById('btn-back-title');
    const btnBackDashboard = document.getElementById('btn-back-dashboard');

    // Detail View Elements
    const detailTitle = document.getElementById('detail-title');
    const detailSlideImg = document.getElementById('detail-slide-img');
    const detailNarrationText = document.getElementById('detail-narration-text');

    // Audio Elements
    const voiceoverAudio = document.getElementById('voiceover-audio');
    const btnPlayAudio = document.getElementById('btn-play-audio');
    const audioProgress = document.getElementById('audio-progress');
    const audioTime = document.getElementById('audio-time');

    const playIcon = btnPlayAudio.querySelector('.play-icon');
    const pauseIcon = btnPlayAudio.querySelector('.pause-icon');

    // Data for Demo Scenarios
    const scenarios = {
        low: {
            title: 'LOW Risk Scenario Analysis',
            img: '../screenshots_experimental/01_low_risk_scenario.png',
            audio: 'voiceovers/03_low_risk.mp3',
            narration: 'First, I will run the LOW Risk scenario. The flight is SV1200 from RUH to JED. There are no major NOTAM restrictions and the weather is stable. The result is: Risk Score: 10, Risk Level: LOW, Recommended Action: PROCEED. This means the flight can continue without human review.'
        },
        medium: {
            title: 'MEDIUM Risk Scenario Analysis',
            img: '../screenshots_experimental/02_medium_risk_scenario.png',
            audio: 'voiceovers/04_medium_risk.mp3',
            narration: 'Next, I will run the MEDIUM Risk scenario. This case includes thunderstorm activity near the route. The result is: Risk Score: 50, Risk Level: MEDIUM, Recommended Action: RE-ROUTE. This shows that the system recommends adjusting the route due to weather risk.'
        },
        high_pending: {
            title: 'HIGH Operational Risk Scenario Analysis (Pending Review)',
            img: '../screenshots_experimental/03_high_risk_pending_review.png',
            audio: 'voiceovers/05_high_risk.mp3',
            narration: 'Now I will run the HIGH Risk scenario. This case includes a runway closure, taxiway restriction, possible ground delays, strong winds, and high temperature. The result is: Risk Score: 80, Risk Level: HIGH, Recommended Action: HOLD. Because this is a high-risk case, the system requires Human-in-the-Loop review.'
        },
        high_approved: {
            title: 'HIGH Operational Risk Scenario Analysis (Approved)',
            img: '../screenshots_experimental/04_high_risk_approved.png',
            audio: 'voiceovers/05_high_risk.mp3',
            narration: 'After human review approval, the system generates the final operational briefing for the HIGH Risk scenario.'
        },
        security_pending: {
            title: 'Security Injection Attack Analysis (Pending Review)',
            img: '../screenshots_experimental/05_security_injection_pending_review.png',
            audio: 'voiceovers/06_security.mp3',
            narration: 'Next, I will test the security layer. This input contains a prompt injection attempt. AeroOps AI detects the unsafe instruction and activates the Security Shield, requiring human review.'
        },
        security_approved: {
            title: 'Security Injection Attack Analysis (Approved)',
            img: '../screenshots_experimental/06_security_injection_approved.png',
            audio: 'voiceovers/06_security.mp3',
            narration: 'After human review, the system generates a security-focused final briefing.'
        },
        invalid: {
            title: 'Invalid Input Validation Test',
            img: '../screenshots_experimental/07_invalid_input_scenario.png',
            audio: 'voiceovers/07_invalid_input.mp3',
            narration: 'Finally, I will test input validation. This case uses an invalid flight number format: 1024. The system rejects the request and returns: Risk Score: 100, Risk Level: HIGH, Recommended Action: CANCEL. The final briefing explains that the flight number must contain two or three letters followed by one to four digits.'
        },
        testing: {
            title: 'Automated Pytest Results',
            img: 'slides/08_testing_results.png',
            audio: 'voiceovers/08_testing.mp3',
            narration: 'The project also includes automated tests. The final test result shows: 11 tests passed. This confirms that the main workflow, validation, risk scoring, and security behavior are working correctly.'
        },
        conclusion: {
            title: 'System Conclusion & Architecture',
            img: '../screenshots_experimental/00_start_page.png',
            audio: 'voiceovers/09_conclusion.mp3',
            narration: 'AeroOps AI demonstrates how agentic AI can support aviation operations while keeping safety, validation, security, deterministic scoring, and human oversight at the center. Thank you.'
        }
    };

    // Transition Helpers
    const showView = (targetView) => {
        // Hide all
        [viewTitle, viewDashboard, viewDetail].forEach(v => {
            v.classList.remove('active');
            setTimeout(() => {
                if (!v.classList.contains('active')) {
                    v.style.display = 'none';
                }
            }, 400);
        });

        // Show target
        targetView.style.display = 'flex';
        setTimeout(() => {
            targetView.classList.add('active');
        }, 50);

        // Stop audio if navigating away from detail view
        if (targetView !== viewDetail) {
            stopAudio();
        }
    };

    // Navigation events
    btnEnter.addEventListener('click', () => showView(viewDashboard));
    btnBackTitle.addEventListener('click', () => showView(viewTitle));
    btnBackDashboard.addEventListener('click', () => showView(viewDashboard));

    // Scenario Select events
    document.querySelectorAll('.demo-select-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetKey = btn.getAttribute('data-target');
            const data = scenarios[targetKey];
            if (data) {
                // Populate details view
                detailTitle.textContent = data.title;
                detailSlideImg.src = data.img;
                detailNarrationText.textContent = data.narration;

                // Configure audio source
                voiceoverAudio.src = data.audio;
                voiceoverAudio.load();

                // Show view
                showView(viewDetail);
            }
        });
    });

    // Audio Play/Pause handlers
    const togglePlay = () => {
        if (voiceoverAudio.paused) {
            voiceoverAudio.play()
                .then(() => {
                    playIcon.classList.add('hidden');
                    pauseIcon.classList.remove('hidden');
                })
                .catch(err => {
                    console.error("Audio play failed:", err);
                });
        } else {
            voiceoverAudio.pause();
            playIcon.classList.remove('hidden');
            pauseIcon.classList.add('hidden');
        }
    };

    const stopAudio = () => {
        voiceoverAudio.pause();
        voiceoverAudio.currentTime = 0;
        playIcon.classList.remove('hidden');
        pauseIcon.classList.add('hidden');
        audioProgress.style.width = '0%';
        audioTime.textContent = '0:00';
    };

    btnPlayAudio.addEventListener('click', togglePlay);

    // Audio progress bar updates
    voiceoverAudio.addEventListener('timeupdate', () => {
        if (voiceoverAudio.duration) {
            const pct = (voiceoverAudio.currentTime / voiceoverAudio.duration) * 100;
            audioProgress.style.width = `${pct}%`;

            // Format time elapsed
            const mins = Math.floor(voiceoverAudio.currentTime / 60);
            const secs = Math.floor(voiceoverAudio.currentTime % 60).toString().padStart(2, '0');
            audioTime.textContent = `${mins}:${secs}`;
        }
    });

    voiceoverAudio.addEventListener('ended', () => {
        playIcon.classList.remove('hidden');
        pauseIcon.classList.add('hidden');
        audioProgress.style.width = '0%';
        audioTime.textContent = '0:00';
    });

    // Seek on progress bar click
    const progressBar = document.querySelector('.audio-progress-bar');
    progressBar.addEventListener('click', (e) => {
        if (voiceoverAudio.duration) {
            const rect = progressBar.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const pct = clickX / rect.width;
            voiceoverAudio.currentTime = pct * voiceoverAudio.duration;
        }
    });
});
