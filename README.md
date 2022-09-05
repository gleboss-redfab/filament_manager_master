# filament-manager-RPi-server
Реализация промежуточной логики обработки REST запросов (еще не сделано) и общения с RP2040 по Modbus RTU протоколу. Скрипт реализует простейший CLI для вызова команд и чтение состояния системы.

## Features:
- Modbus RTU Master
- RS-485
- Описание команд и их параметров в [Notion](https://ultra-pearl-ffc.notion.site/644a55b5df064eafa0bd0780ddef2003)
- 

## How to use firmware:
1. подключиться по SSH к малине
2. подключить RS-485 свисток и витую пару до принимающей платы
3.
```
/bin/python /home/gleboss11/modbus_test_usb_rs485/modbus_master.py
```

## TODO:
- обрабюотку REST запросов
- REST клиент в Swager или как там его

