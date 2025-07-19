
document.addEventListener('DOMContentLoaded', () => {
    const connectBtn = document.getElementById('connect_btn');
    const ipAddressInput = document.getElementById('ip_address');
    const controls = document.getElementById('controls');
    const output = document.getElementById('output');

    const uninstallAppBtn = document.getElementById('uninstall_app_btn');
    const packageNameInput = document.getElementById('package_name');
    const installAppBtn = document.getElementById('install_app_btn');
    const apkFileInput = document.getElementById('apk_file');

    connectBtn.addEventListener('click', async () => {
        const ip_address = ipAddressInput.value.trim();
        if (!ip_address) {
            alert('Please enter an IP address.');
            return;
        }

        const response = await fetch('/connect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ip_address })
        });

        const result = await response.json();
        output.textContent = result.message;

        if (result.success) {
            controls.classList.remove('hidden');
        }
    });

    async function runAdbCommand(command) {
        const response = await fetch('/adb', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command })
        });

        const result = await response.json();
        output.textContent = result.output;
    }

    uninstallAppBtn.addEventListener('click', () => {
        const packageName = packageNameInput.value.trim();
        if (!packageName) {
            alert('Please enter a package name.');
            return;
        }
        runAdbCommand(`uninstall ${packageName}`);
    });

    installAppBtn.addEventListener('click', () => {
        const file = apkFileInput.files[0];
        if (!file) {
            alert('Please select an APK file.');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = async (e) => {
            const formData = new FormData();
            formData.append('apk', file);

            // This part requires a dedicated endpoint for file uploads
            // For simplicity, this example will not fully implement file uploads
            // but will show the command.
            alert('File upload not implemented in this demo. Command would be: adb install <path_to_apk>');
            // In a real app, you would upload the file and then run:
            // runAdbCommand(`install /path/to/uploaded/apk`);
        };
        reader.readAsDataURL(file);
    });
});
