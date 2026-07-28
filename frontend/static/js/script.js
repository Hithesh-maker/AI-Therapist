const video = document.getElementById('webcam');
const output = document.getElementById('output');

const faceEmotionPanel = document.getElementById('faceEmotionPanel');
const faceEmotionText = document.getElementById('faceEmotionText');
const faceEmojiDisplay = document.getElementById('faceEmojiDisplay');

const voiceEmotionPanel = document.getElementById('voiceEmotionPanel');
const voiceEmotionText = document.getElementById('voiceEmotionText');
const voiceEmojiDisplay = document.getElementById('voiceEmojiDisplay');
const voiceStatus = document.getElementById('voiceStatus');


// ✅ Render Backend URL
const BACKEND_URL = "https://ai-therapist-hkt5.onrender.com";


let mediaRecorder;
let audioChunks = [];


// Start webcam once
navigator.mediaDevices.getUserMedia({ video: true, audio: true })
.then(stream => {

    video.srcObject = stream;

    output.classList.remove('typing');
    output.innerText = "✅ Webcam is working.";


    mediaRecorder = new MediaRecorder(stream);


    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };


    mediaRecorder.onstop = () => {

        const audioBlob = new Blob(audioChunks, {
            type: 'audio/wav'
        });

        audioChunks = [];

        sendVoiceToBackend(audioBlob);
    };


})
.catch(err => {

    console.error("Webcam/Audio error:", err);

    output.innerText =
        "❌ Error: " + err.message;

});




// Face Emotion Detection
function captureAndSend() {


    output.innerText = "Analyzing Face...";

    output.classList.add('typing');

    faceEmotionPanel.style.display = 'none';



    const canvas = document.createElement('canvas');

    canvas.width = 320;
    canvas.height = 240;


    const ctx = canvas.getContext('2d');

    ctx.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );


    const imageData = canvas.toDataURL('image/jpeg');



    fetch(`${BACKEND_URL}/predict`, {

        method: 'POST',

        headers: {
            'Content-Type': 'application/json'
        },

        body: JSON.stringify({
            image: imageData
        })

    })


    .then(res => res.json())


    .then(data => {


        output.classList.remove('typing');

        output.innerText =
            "✅ Face Analysis complete.";



        const emotion =
            data.emotion || "Unknown";


        const score =
            data.score !== undefined
            ? data.score
            : "N/A";



        faceEmotionText.innerText =
            `${emotion} (Score: ${score}%)`;



        faceEmojiDisplay.innerText =
            mapEmotionToEmoji(emotion);



        faceEmotionPanel.style.display =
            "block";


    })


    .catch(err => {


        console.error(err);


        output.classList.remove('typing');


        output.innerText =
            "❌ Face Analysis Failed: " + err.message;


    });


}





// Voice Recording

document.getElementById('recordBtn')
.addEventListener('click', () => {


    if(mediaRecorder && mediaRecorder.state === 'inactive') {


        voiceStatus.innerText =
            "🎙️ Recording Voice Emotion...";


        mediaRecorder.start();



        setTimeout(() => {


            mediaRecorder.stop();


            voiceStatus.innerText =
                "🔄 Processing Voice...";


        },4000);


    }


});







// Send Voice To Backend

function sendVoiceToBackend(audioBlob) {


    const formData = new FormData();


    formData.append(
        'audio',
        audioBlob,
        'audio.wav'
    );



    fetch(`${BACKEND_URL}/predict_voice`, {

        method:'POST',

        body:formData

    })


    .then(res => res.json())


    .then(data => {


        voiceStatus.innerText =
            "✅ Voice Analysis complete.";



        const emotion =
            data.emotion || "Unknown";



        const confidence =
            data.confidence !== undefined
            ? data.confidence
            : "N/A";



        voiceEmotionText.innerText =
            `${emotion} (Confidence: ${confidence}%)`;



        voiceEmojiDisplay.innerText =
            mapEmotionToEmoji(emotion);



        voiceEmotionPanel.style.display =
            "block";


    })


    .catch(err => {


        console.error(err);


        voiceStatus.innerText =
            "❌ Voice Analysis Failed: " + err.message;


    });


}







// Emoji Mapping

function mapEmotionToEmoji(emotion) {


    const map = {


        happy:"😊",

        sad:"😢",

        angry:"😠",

        surprised:"😲",

        neutral:"😐",

        fear:"😨",

        disgust:"🤢",

        confused:"😕",

        tired:"🥱"


    };


    return map[emotion.toLowerCase()] || "🤖";

}