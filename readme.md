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
