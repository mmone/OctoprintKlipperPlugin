# OctoPrint Klipper Plugin

This plugin assists in managing and monitoring the [Klipper](https://github.com/KevinOConnor/klipper) 3D printer firmware.

### Features
- Simplified connection dialog.
- Restart Host and MCU processes.
- User defineable macro buttons.
- Assisted bed leveling wizard with user definable probe points.
- PID Tuning Dialog.
- Message log displaying messages from Klipper prepended with "//" and "!!".

### Status
Usable

### ToDo
- On first install automatically check/add virtual serialport as descriped [here](https://github.com/KevinOConnor/klipper/blob/master/docs/Installation.md#configuring-octoprint-to-use-klipper) in the klipper docs. You need to do this manually for now if you haven't already.
- Add a continously updated status display in octoprints navbar.

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/mmone/OctoPrintKlipper/archive/master.zip


## Configuration

Click on the wrench icon in the titlebar to open OctoPrints settings dialog. Select "Klipper" at the bottom of the settings dialog.
