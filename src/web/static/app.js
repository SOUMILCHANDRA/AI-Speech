document.addEventListener('DOMContentLoaded', () => {
    const recordBtn = document.getElementById('recordBtn');
    const statusText = document.getElementById('statusText');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const audioPlayback = document.getElementById('audioPlayback');
    const resultSection = document.getElementById('resultSection');
    const metricsGrid = document.getElementById('metricsGrid');
    const aiFeedback = document.getElementById('aiFeedback');
    const playTtsBtn = document.getElementById('playTtsBtn');
    const transcriptText = document.getElementById('transcriptText');
    const overallScoreElement = document.getElementById('overallScore');

    const fileInput = document.getElementById('fileInput');

    let mediaRecorder;
    let audioChunks = [];
    let audioBlob = null;
    let isRecording = false;

    // File Upload Logic
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            audioBlob = null; // Clear recording blob
            statusText.textContent = `Selected: ${e.target.files[0].name}`;
            analyzeBtn.disabled = false;

            // Set playback
            const audioUrl = URL.createObjectURL(e.target.files[0]);
            audioPlayback.src = audioUrl;
            audioPlayback.hidden = false;
        }
    });

    // Recording Logic
    recordBtn.addEventListener('click', async () => {
        if (!isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
    });

    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            // Clear file input
            fileInput.value = '';

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(audioBlob);
                audioPlayback.src = audioUrl;
                audioPlayback.hidden = false;
                analyzeBtn.disabled = false;
                statusText.textContent = "Recording Saved. Ready to Analyze.";
            };

            mediaRecorder.start();
            isRecording = true;
            recordBtn.classList.add('recording');
            statusText.textContent = "Listening... (Tap to Stop)";

            // Visualizer logic (mock for now or basic canvas)
        } catch (err) {
            alert("Microphone access denied or error: " + err);
        }
    }

    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
        }
        isRecording = false;
        recordBtn.classList.remove('recording');
    }

    // Analysis Logic
    analyzeBtn.addEventListener('click', async () => {
        const file = fileInput.files[0];

        // Either audioBlob (rec) or file (upload) must exist
        if (!audioBlob && !file) return;

        analyzeBtn.disabled = true;
        analyzeBtn.textContent = "Analyzing...";
        statusText.textContent = "AI is evaluating speech...";
        resultSection.classList.add('hidden');

        const formData = new FormData();

        if (file) {
            formData.append('audio', file, file.name);
        } else {
            formData.append('audio', audioBlob, 'recording.wav');
        }

        const language = document.getElementById('languageSelect').value;
        const modelSize = document.getElementById('modelSelect').value;

        formData.append('language', language);
        formData.append('model_size', modelSize);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || "Analysis failed");
            }

            const data = await response.json();
            displayResults(data);

        } catch (err) {
            alert("Error: " + err);
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = "Analyze Recording";
            statusText.textContent = "Analysis Complete";
        }
    });

    function displayResults(data) {
        resultSection.classList.remove('hidden');

        // 1. Transcript
        transcriptText.textContent = data.transcript;

        // 2. Metrics (inject cards)
        metricsGrid.innerHTML = '';

        // Helper for safe formatting
        const fmt = (val, fixed = 1) => (val !== undefined && val !== null) ? val.toFixed(fixed) : "-";

        const metrics = [
            { label: "Duration", val: fmt(data.metrics.acoustic.duration_sec, 1) + "s" },
            { label: "WPM", val: fmt(data.metrics.text.wpm, 0) },
            { label: "Pitch (Hz)", val: fmt(data.metrics.acoustic.pitch_mean_hz, 0) },
            { label: "Pitch Var", val: fmt(data.metrics.acoustic.pitch_std_hz, 0) },
            { label: "Pauses", val: fmt(data.metrics.acoustic.pause_fraction * 100, 1) + "%" }
        ];

        metrics.forEach(m => {
            const card = document.createElement('div');
            card.className = 'metric-card';
            card.innerHTML = `<span class="metric-val">${m.val}</span><span class="metric-label">${m.label}</span>`;
            metricsGrid.appendChild(card);
        });

        // 3. AI Report
        const report = data.report;
        if (report.overall_summary) {
            aiFeedback.textContent = report.overall_summary;
        } else {
            // Fallback content if summary missing
            aiFeedback.textContent = JSON.stringify(report.ratings, null, 2);
        }

        // Calculate simple overall average score if not present
        let total = 0;
        let count = 0;
        if (report.ratings) {
            for (let k in report.ratings) {
                total += report.ratings[k].score;
                count++;
            }
        }
        const avg = count ? (total / count).toFixed(1) : "?";
        overallScoreElement.textContent = avg;
    }

    // TTS Logic
    playTtsBtn.addEventListener('click', async () => {
        const text = aiFeedback.textContent;
        if (!text) return;

        playTtsBtn.disabled = true;
        playTtsBtn.textContent = "Generating Audio...";

        try {
            const res = await fetch('/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: text,
                    voice: 'en-IN-NeerjaNeural'
                })
            });

            const data = await res.json();
            if (data.audio_url) {
                const audio = new Audio(data.audio_url);
                audio.play();
            }
        } catch (err) {
            alert("TTS Error: " + err);
        } finally {
            playTtsBtn.disabled = false;
            playTtsBtn.textContent = "🔊 Listen to Feedback";
        }
    });

});
