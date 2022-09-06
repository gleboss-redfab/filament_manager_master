from modbus_manager import ModbusManager
from modbus_manager import commands as mb_commands
from modbus_manager import statuses as mb_statuses
from modbus_manager import busy_codes as mb_busy_codes
from modbus_manager import error_codes as mb_error_codes



mb_manager = ModbusManager()

# начинаем бесконечно парсить командную строку, ждать команды
while(True):
    command_str = input("write command: ")

    if command_str.isdigit():
        command = int(command_str)
    else:
        command = command_str

    if(command in mb_commands.keys()):
        # считываем лист параметров через пробел 
        command_parameters = list(map(int, input("write parameters: ").split()))
        print(mb_commands[command] +" with params: " + str(command_parameters))

        mb_manager.send_command(command, command_parameters)

    elif(command == "state"):
        mb_manager.read_state()
        
    elif(command == "state full"):
        mb_manager.read_state_full()   

