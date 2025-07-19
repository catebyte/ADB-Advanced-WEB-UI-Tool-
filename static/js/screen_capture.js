document.addEventListener('DOMContentLoaded', () => {
    const screenshotBtn = document.getElementById('screenshot_btn');
    const screenrecordBtn = document.getElementById('screenrecord_btn');
    const stopScreenrecordBtn = document.getElementById('stop_screenrecord_btn');
    const previewContainer = document.getElementById('preview_container');

    screenshotBtn.addEventListener('click', async () => {
        const response = await fetch('/screenshot');
        const result = await response.json();

        if (result.success) {
            previewContainer.innerHTML = `<img src="${result.file_path}" width="100%">`;
        } else {
            previewContainer.innerHTML = `<p>Error: ${result.error}</p>`;
        }
    });

    screenrecordBtn.addEventListener('click', async () => {
        const response = await fetch('/screenrecord/start');
        const result = await response.json();

        if (result.success) {
            screenrecordBtn.classList.add('hidden');
            stopScreenrecordBtn.classList.remove('hidden');
            previewContainer.innerHTML = '<p>Recording...</p>';
        } else {
            previewContainer.innerHTML = `<p>Error: ${result.error}</p>`;
        }
    });

    stopScreenrecordBtn.addEventListener('click', async () => {
        const response = await fetch('/screenrecord/stop');
        const result = await response.json();

        if (result.success) {
            screenrecordBtn.classList.remove('hidden');
            stopScreenrecordBtn.classList.add('hidden');
            previewContainer.innerHTML = `<video width="100%" controls><source src="${result.file_path}" type="video/mp4"></video>`;
        } else {
            previewContainer.innerHTML = `<p>Error: ${result.error}</p>`;
        }
    });
});