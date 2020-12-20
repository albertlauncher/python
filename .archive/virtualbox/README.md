# Python virtualbox


```bash
cd /usr/lib/virtualbox
URL="https://download.virtualbox.org/virtualbox/6.1.16/VirtualBoxSDK-6.1.16-140961.zip"
wget "$URL"
unzip $(basename $URL)

cd sdk/installer

export VBOX_INSTALL_PATH=/usr/lib/virtualbox
export VBOX_SDK_PATH=/usr/lib/virtualbox/sdk
export PYTHONPATH=/usr/lib/virtualbox/sdk/bindings/xpcom/python
python vboxapisetup.py install


Gave it up here

```
