"""
Module Name:  d2cMsgSender.py
Project:      IoTHubRestSample
Copyright (c) Microsoft Corporation.

Using [Send device-to-cloud message](https://msdn.microsoft.com/en-US/library/azure/mt590784.aspx) API to send device-to-cloud message from the simulated device application to IoT Hub.

This source is subject to the Microsoft Public License.
See http://www.microsoft.com/en-us/openness/licenses.aspx#MPL
All other rights reserved.

THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, 
EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.
"""

import base64
import hmac
import hashlib
import time
import requests
import urllib
import random

class D2CMsgSender:
    
    API_VERSION = '2016-02-03'
    TOKEN_VALID_SECS = 10
    TOKEN_FORMAT = 'SharedAccessSignature sig=%s&se=%s&skn=%s&sr=%s'
    
    def __init__(self, connectionString=None):
        if connectionString != None:
            iotHost, keyName, keyValue = [sub[sub.index('=') + 1:] for sub in connectionString.split(";")]
            self.iotHost = iotHost
            self.keyName = keyName
            self.keyValue = keyValue
            
    def _buildExpiryOn(self):
        return '%d' % (time.time() + self.TOKEN_VALID_SECS)
    
    def _buildIoTHubSasToken(self, deviceId):
        resourceUri = '%s/devices/%s' % (self.iotHost, deviceId)
        targetUri = resourceUri.lower()
        expiryTime = self._buildExpiryOn()
        toSign = '%s\n%s' % (targetUri, expiryTime)
        key = base64.b64decode(self.keyValue.encode('utf-8'))
        signature = urllib.quote(
            base64.b64encode(
                hmac.HMAC(key, toSign.encode('utf-8'), hashlib.sha256).digest()
            )
        ).replace('/', '%2F')
        return self.TOKEN_FORMAT % (signature, expiryTime, self.keyName, targetUri)
    
    def sendD2CMsg(self, deviceId, message):
        sasToken = self._buildIoTHubSasToken(deviceId)
        url = 'https://%s/devices/%s/messages/events?api-version=%s' % (self.iotHost, deviceId, self.API_VERSION)
        r = requests.post(url, headers={'Authorization': sasToken}, data=message)
        return r.text, r.status_code
    
    def sendIncrementalTemp(self,deviceId):
        startTemp=50.0
        startHumid=50
        startExtTemp=55
        endTemp=70.0
        currentTemp=startTemp
        currentHumid=startHumid
        currentExtTemp=startExtTemp
        while (currentTemp < endTemp):
            randsignno=random.random()>0.6
            randsign=1
            if randsignno:
                randsign=-1
            else:
                randsign=1
            currentTemp = currentTemp + random.random()*randsign/2
            currentHumid= currentHumid + random.random()*randsign/2
            currentExtTemp= currentExtTemp + random.random()*randsign/2
            
            print currentTemp
            message2='{"DeviceId":"'+deviceId+'", "Temperature":'+str(currentTemp)+', "Humidity":'+str(currentHumid)+', "ExternalTemperature":'+str(currentExtTemp)+'}'
            print d2cMsgSender.sendD2CMsg(deviceId, message2)
        
            
            
if __name__ == '__main__':
    connectionString = 'HostName=ckmilahatest1.azure-devices.net;SharedAccessKeyName=device;SharedAccessKey=U0dqvwKDDzdQeTTiEqU0KmX3AZD9zcSm791ilLIculk='
    d2cMsgSender = D2CMsgSender(connectionString)
    deviceId = 'raspberry'
    message1 = '{"ObjectType":"DeviceInfo", "Version":"1.0", "IsSimulatedDevice":false, "DeviceProperties": { "DeviceID":"raspberry", "HubEnabledState":true }, "Commands": [ {"Name":"SetHumidity", "Parameters":[{"Name":"humidity","Type":"double"}]}, { "Name":"SetTemperature", "Parameters":[{"Name":"temperature","Type":"double"}]} ] }'
    print d2cMsgSender.sendD2CMsg(deviceId, message1)
    
    d2cMsgSender.sendIncrementalTemp(deviceId)
"""   
    message2='{"DeviceId":"raspberry", "Temperature":50, "Humidity":50, "ExternalTemperature":55}'
    print d2cMsgSender.sendD2CMsg(deviceId, message2)
"""
