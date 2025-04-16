console.log("✅ script.js loaded");

document.addEventListener("DOMContentLoaded", function () {
    console.log("script.js loaded"); // ✅ Confirm the script is actually loading

    // === PDF Upload ===
    const pdfForm = document.getElementById("pdfForm");
    const pdfInput = document.getElementById("book");

    if (pdfForm && pdfInput) {
        pdfForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const file = pdfInput.files[0];

            if (!file) {
                alert("Please select a PDF file.");
                return;
            }

            console.log("PDF file selected:", file.name);
            const formData = new FormData();
            formData.append("pdf", file);

            fetch("/upload_pdf", {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log("Upload response:", data);
                if (data.error) {
                    alert("Error uploading PDF: " + data.error);
                } else {
                    alert("PDF uploaded and parsed successfully!");
                    document.getElementById('pdfFilename').textContent = `📄 Uploaded File: ${file.name}`;
                }
            })
            .catch(error => {
                console.error("Error uploading PDF:", error);
                alert("Something went wrong uploading the PDF.");
            });
        });
    } else {
        console.error("PDF form or input not found in DOM.");
    }

    // === Audio Q&A ===
    const recordButton = document.getElementById('record');
    const stopButton = document.getElementById('stop');
    const transcriptionDiv = document.getElementById('transcription');
    const answerDiv = document.getElementById('answer');
    const responseAudio = document.getElementById('responseAudio');
    const recordedFilesList = document.getElementById('recordedFiles');

    let mediaRecorder;
    let audioChunks = [];

    if (recordButton && stopButton) {
        recordButton.addEventListener('click', () => {
            console.log("Start Recording clicked");
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    mediaRecorder = new MediaRecorder(stream);
                    mediaRecorder.start();
                    audioChunks = [];
                    mediaRecorder.ondataavailable = event => {
                        audioChunks.push(event.data);
                    };
                    recordButton.disabled = true;
                    stopButton.disabled = false;
                })
                .catch(error => {
                    console.error("Microphone access denied:", error);
                    alert("Microphone access denied. Please allow microphone permissions.");
                });
        });

        stopButton.addEventListener('click', () => {
            if (mediaRecorder && mediaRecorder.state !== "inactive") {
                mediaRecorder.stop();
                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    const formData = new FormData();
                    formData.append('audio_data', audioBlob, 'recorded_audio.webm');

                    fetch('/upload', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            transcriptionDiv.textContent = "Error: " + data.error;
                            answerDiv.textContent = "";
                            responseAudio.src = "";
                        } else {
                            transcriptionDiv.textContent = "Transcript: " + data.result;
                            answerDiv.textContent = "AI Answer: " + data.answer;
                            responseAudio.src = data.audio_url;
                            responseAudio.load();

                            const li = document.createElement('li');
                            li.innerHTML = `
                                Transcript: ${data.result} <br>
                                Answer: ${data.answer} <br>
                                <audio controls src="${data.audio_url}"></audio>
                            `;
                            recordedFilesList.appendChild(li);
                        }
                    })
                    .catch(error => {
                        console.error("Error uploading audio:", error);
                        transcriptionDiv.textContent = "Error uploading audio.";
                        answerDiv.textContent = "";
                        responseAudio.src = "";
                    });
                };
            }

            recordButton.disabled = false;
            stopButton.disabled = true;
        });
    } else {
        console.error("Record or Stop button not found.");
    }
});
