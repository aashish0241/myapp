[app]
title = SMS OTP Reader
package.name = smsotpreader
package.domain = sms.reader
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
requirements = python3,kivy,pyjnius
android.permissions = RECEIVE_SMS,READ_SMS,INTERNET,READ_PHONE_STATE
android.minapi = 21
android.api = 28
android.services = sms_service:service.py
orientation = portrait

[buildozer]
log_level = 2
