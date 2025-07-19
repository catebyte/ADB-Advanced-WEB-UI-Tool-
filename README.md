# ADB WebUI

A simple, intuitive web-based interface for managing Android devices with the Android Debug Bridge (ADB).

![Screenshot of the main page](images/Home%20Page.png)

## Features

*   **Web-Based UI:** Control your Android device from your web browser.
*   **File Manager:** Browse, view, and delete files on your device.
*   **App Management:** List and uninstall installed applications.
*   **Screen Capture:** Take screenshots and record the screen of your device.
*   **Live Screen Sharing:** View your device's screen in real-time in your browser.
*   **Shell Execute:** Run any ADB shell command directly from the UI.

## Screenshots

| File Manager | App Management | Screen Capture |
| :---: | :---: | :---: |
| ![File Manager](images/screenshot2.png) | ![App Management](images/screenshot3.png) | ![Screen Capture](images/screenshot4.png) |

## Installation

1.  **Prerequisites:**
    *   Python 3.6+
    *   ADB (Android Debug Bridge) installed and in your system's PATH.

2.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/adb-webui.git
    cd adb-webui
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the application:**

    ```bash
    python app.py
    ```

2.  **Open your web browser** and navigate to `http://127.0.0.1:5000`.

3.  **Login** with the default credentials:
    *   **Username:** `admin`
    *   **Password:** `admin`

4.  **Connect to your device:**
    *   Enable ADB debugging on your Android device.
    *   Connect your device to your computer via USB or Wi-Fi.
    *   Enter your device's IP address in the WebUI and click "Connect".

## How to Contribute

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
