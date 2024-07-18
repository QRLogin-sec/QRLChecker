# QRLChecker

**Note that the code is available currently for paper review. Considering the possible abuse of QRLChecker on potentially vulnerable websites in real world, we will make the code available only to vetted researchers upon request when publishing this paper.**

### Configuration

Set up the `config.ini` file to specify the personal information used for detection.

Configure `mitmproxy` on the mobile phone, setting the proxy port to 7778.

### Running

Use the following command to run QRLChecker, replacing `<URL>` with the URL of the website to be tested:

```shell
./run.sh <URL>
```

### Structure

```
QRLChecker/
├── components/
│   ├── components.py	# Initializes key components 
│   ├── app_flow_manager.py	# Manages traffic of QRLogin app and app authorization requests
│   ├── polling_manager.py	# Manages polling requests including url, flows, replayed flows, etc.
│   └── qrcode_manager.py	# Manages variables and operations related to QR code
├── config/
│   ├── logger_config.py	# Configures a logger
│   └── webdriver_config.py	# Configures a selenium webdriver with proxy settings
├── logs/
│   └── log_xxx.log		# Generated logs
├── res/
│   └── res_xxx.txt		# Flaw detection results
├── analyzer.py			# Analyzes traffic and identifies key components
├── detector.py			# Detects six flaws based on identified components
├── qrcode_handler.py		# Captures and decoodes QR code
├── traffic_recorder.py		# Records traffic
├── utils.py		
├── run.sh
├── config.ini
├── README.md
└── .gitignore

```
