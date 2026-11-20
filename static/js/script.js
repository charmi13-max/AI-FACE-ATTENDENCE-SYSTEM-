const video = document.getElementById('video');
const captureBtn = document.getElementById('captureBtn');
const resultBox = document.getElementById('result');
const canvas = document.getElementById('captureCanvas');

async function startCamera() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    resultBox.textContent = 'Camera access is not supported in this browser.';
    resultBox.classList.remove('hidden');
    resultBox.classList.add('error');
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    video.srcObject = stream;
  } catch (error) {
    resultBox.textContent = 'Unable to access the camera. Please allow camera permissions.';
    resultBox.classList.remove('hidden');
    resultBox.classList.add('error');
  }
}

captureBtn.addEventListener('click', async () => {
  const context = canvas.getContext('2d');
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  const imageData = canvas.toDataURL('image/png');

  const response = await fetch('/attendance/mark', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    },
    body: new URLSearchParams({ image: imageData })
  });

  const data = await response.json();
  resultBox.classList.remove('hidden');

  if (response.ok) {
    resultBox.classList.remove('error');
    resultBox.classList.add('success');
  } else {
    resultBox.classList.remove('success');
    resultBox.classList.add('error');
  }

  resultBox.textContent = data.message || 'Unknown result';
});

startCamera();
