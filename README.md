# OctoPrint Klipper Plugin

This plugin assists in managing and monitoring the [Klipper](https://github.com/KevinOConnor/klipper) 3D printer firmware.

### Features
- Simplified connection dialog.
- Restart Host and MCU processes.
- User defineable macro buttons.
- Assisted bed leveling wizard with user definable probe points.
- PID Tuning Dialog.
- Dialog to set a coordinate offset for future GCODE move commands.
- Message log displaying messages from Klipper prepended with "//" and "!!".

### ToDo
- Add a continously updated status display in octoprints navbar.

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/mmone/OctoPrintKlipper/archive/master.zip


## Configuration

Click on the wrench icon in the titlebar to open OctoPrints settings dialog. Select "Klipper" at the bottom of the settings dialog.

## Contributions

Also for the moment this plugin does what I wanted it to do, it is far from finished, pull requests are welcome. If you want to get started, the OctoPrint Plugin API is quite well documented here: [docs.octoprint.org/en/master/plugins](http://docs.octoprint.org/en/master/plugins).


## Screenshots

#### Message Log
![Message Log](docs/assets/img/message-log.png)

#### Bed Leveling
![Bed Leveling](docs/assets/img/bed-leveling.png)

#### PID Tuning
![PID Tuning](docs/assets/img/pid-tuning.png)

#### Coordinate Offset
![Coordinate Offset](docs/assets/img/offset.png)

#### Settings
![Settings](docs/assets/img/settings.png)
