document.addEventListener('DOMContentLoaded', () => {
    const executeBtn = document.getElementById('execute_btn');
    const shellCommandInput = document.getElementById('shell_command');
    const output = document.getElementById('output');

    async function runShellCommand(command) {
        const response = await fetch('/adb', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: `shell ${command}` })
        });

        const result = await response.json();
        output.textContent = result.output;
    }

    executeBtn.addEventListener('click', () => {
        const command = shellCommandInput.value.trim();
        if (!command) {
            alert('Please enter a command.');
            return;
        }
        runShellCommand(command);
    });
});