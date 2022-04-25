# Hacktribe Editor

An editor app for hacktribe

## Features
 - GUI
 - Patch firmware

<br/>

To test:

Clone hacktribe:

    git clone https://github.com/bangcorrupt/hacktribe.git

Move to `app` directory:

    cd hacktribe/app

Install dependencies:

    pip install -r requirements.txt

Run `hacktribe_app_gui.py`:

    python hacktribe_app_gui.py

Follow the instructions in the app, pay attention to the log output in the text box.

<br/>

Installation of bsdiff4 will fail on Windows without the correct build tools installed, see [#103](https://github.com/bangcorrupt/hacktribe/issues/103).

An [executable](https://github.com/bangcorrupt/hacktribe/blob/main/app/hacktribe-gui.exe) is available for Windows.


