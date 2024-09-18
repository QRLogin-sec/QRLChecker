# ARTIFACTS

We comply with the open science policy by sharing our artifacts including the source code of detection pipeline and auditing tool, QRLChecker, as well as the dataset and the scripts for collecting QRLogin webstes.

**Note that the code is available currently for paper review. To avoid potential abuse on real-world websites, we will make the code available only to vetted researchers or developers upon request and identity verification when publishing this paper.**



## Detection Pipeline

#### Configuration

Set up the `credential.ini` file to specify the personal information used for detection.

Ensure `mitmproxy` and `selenium` are set up.

Configure `mitmproxy` on the mobile phone, setting the proxy port to 7778.

#### Running

Use the following command to run QRLChecker, replacing `<URL>` with the URL of the website to be tested:

```shell
./run_pipeline.sh <URL>
```

#### Structure

```
detection_pipeline/
├── components/
│   ├── components.py		# Initializes key components 
│   ├── app_flow_manager.py	# Manages traffic of QRLogin app and app authorization requests
│   ├── polling_manager.py	# Manages polling requests including url, flows, replayed flows, etc.
│   └── qrcode_manager.py	# Manages variables and operations related to QR code
├── config/
│   ├── logger_config.py	# Configures a logger
│   └── webdriver_config.py	# Configures a selenium webdriver with proxy settings
├── intermediate_files/
│   └── done_flag.txt            # Generated flag of QRLogin completion
├── logs/
│   └── log_xxx.log		# Generated logs
├── res/
│   └── res_xxx.txt		# Flaw detection results
├── analyzer.py			# Analyzes traffic and identifies key components
├── detector.py			# Detects six flaws based on identified components
├── qrcode_handler.py		# Captures and decoodes QR code
├── traffic_recorder.py		# Records traffic
├── utils.py
├── run_pipeline.sh
└── credential.ini		# Credentials to be detected
```



## Auditing Tool - QRLChecker

#### Configuration

Set up the `credential.ini` file to specify the personal information used for detection.

Developers need to prepare `configuration.json` file to specify the components in QRLogin implementations.

Ensure `mitmproxy` and `selenium` are set up.

Configure `mitmproxy` on the mobile phone, setting the proxy port to 7778.

#### Running

Use the following command to run QRLChecker, replacing `<URL>` with the URL of the website to be tested:

```shell
./run_qrlchecker.sh <URL>
```

#### Structure

```
QRLChecker/
├── components/
│   ├── components.py            # Initializes key components 
│   ├── app_flow_manager.py      # Manages traffic of QRLogin app and app authorization requests
│   ├── polling_manager.py       # Manages polling requests including url, flows, replayed flows, etc.
│   └── qrcode_manager.py        # Manages variables and operations related to QR code
├── config/
│   ├── credential.ini	         # Credentials to be detected
│   ├── configuration.json       # Configurations of QRLogin provided by developer as input
│   ├── logger_config.py         # Configures a logger
│   ├── flaws_mitigations.py     # Defines flaws and corresponding mitigations
│   └── webdriver_config.py      # Configures a selenium webdriver with proxy settings
├── intermediate_files/
│   └── done_flag.txt            # Generated flag of QRLogin completion
├── logs/
│   └── log_xxx.log              # Generated logs
├── res/
│   └── res_xxx.txt              # Flaw detection results
├── reports/
│   └── report_xxx.md            # Generated auditing reports for developers
├── initialization.py            # Read configuration and locate key components in traffic
├── detection.py                 # Detects six flaws
├── qrlogin_process.py           # Initiates the QR code login process
├── traffic_recorder.py          # Records traffic
├── utils.py
└── run_qrlchecker.sh
```



## Scripts for Collecting QRLogin Websites

#### Configuration

Configure the relevant file paths in the `config/params.py` file.

Configure the `data/input/websites.csv` file by entering website domain names in the prescribed format.

#### Running

After configuring as mentioned above, execute the required operations in `bin/run.py`.

#### Structure

```
QRLogin_website_collection/
├── bin
│   ├── run.py                         # Start Script
├── common
│   ├── utils.py                       # Shared Methods in the Project
├── config
│   ├── constants.py                   # Static Configuration
|   ├── params.py                      # Dynamic Configuration
├── data 
│   ├── inputs                         # Project Inputs
│   |   ├── websites.csv                     # Populate the website dataset
|   ├── logs                           # Log Files for Each Stage
|   |    └── xxx.log 
│   ├── outputs                        # Project Outputs
│   |   ├── extrat_text                      # Text Content Extracted from HTML
|   |   |    └── xxx.txt
│   |   ├── extrat_text_en                   # Translating all non-English content in the text to English
|   |   |    └── xxx_en.txt
│   |   ├── html                             # Login pages collected based on the input
|   |   |    └── xxx.html
│   |   ├── screemshot                       # Screenshot of the login interface.
|   |   |    └── xxx.png
│   |   ├── translation_record.csv           # Translation Records
│   |   ├── QRlogn_websites.csv              # Recognition Results
├── src
│   ├── assets  
│   |   ├── SVM_login.pkl                    # Model Files from [9]
│   ├── extraxt_text_from_html.py      # Extracting the required text from HTML
│   ├── find_login_page.py             # Collected Login Pages
│   ├── is_login_page.py               # Determining if it is a login page
│   ├── search_keywords_in_file.py     # Identifying if it is QRLogin
│   ├── translate_non_english_text.py  # Translate non-English content in the text
```


## Dataset

Tranco top 100K list in `tranco-top-10w.csv`.
