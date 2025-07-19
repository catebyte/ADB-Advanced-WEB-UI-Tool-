document.addEventListener('DOMContentLoaded', () => {
    const listAppsBtn = document.getElementById('list_apps_btn');
    const appsListContainer = document.getElementById('apps_list_container');
    const uninstallAppBtn = document.getElementById('uninstall_app_btn');
    const packageNameInput = document.getElementById('package_name');
    const installAppBtn = document.getElementById('install_app_btn');
    const apkFileInput = document.getElementById('apk_file');
    const output = document.getElementById('output');

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

    listAppsBtn.addEventListener('click', async () => {
        const response = await fetch('/list_apps');
        const result = await response.json();

        if (result.success) {
            let appsHtml = '<table>';
            result.apps.forEach(app => {
                appsHtml += `<tr><td>${app}</td><td><button class="btn btn-sm btn-danger uninstall-btn" data-package="${app}">Uninstall</button></td></tr>`;
            });
            appsHtml += '</table>';
            appsListContainer.innerHTML = appsHtml;
        } else {
            appsListContainer.innerHTML = `<p>Error: ${result.error}</p>`;
        }
    });

    appsListContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('uninstall-btn')) {
            const packageName = e.target.dataset.package;
            packageNameInput.value = packageName;
            uninstallAppBtn.click();
        }
    });

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