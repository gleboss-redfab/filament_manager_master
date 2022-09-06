from sqlite3 import connect
import pymodbus
from pymodbus.pdu import ModbusRequest
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer

from time import sleep

commands= {  0: "COMMAND_IDLE",                 
                    1:"COMMAND_SELECTOR_GO_HOME",     
                    2:"COMMAND_SELECTOR_SELECT_CELL", 
                    3:"COMMAND_FEED_FORWARD",         
                    4:"COMMAND_FEED_BACKWARD",        
                    5:"COMMAND_CUTTER_HOME",          
                    6:"COMMAND_CUTTER_ROTATE",        
                    10:"COMMAND_LOAD_CELL",            
                    11:"COMMAND_UNLOAD_CELL",          
                    100:"COMMAND_INIT",                 
                    101:"COMMAND_INIT_DEFAULT" }           

statuses = {     0:"STATUS_IDLE",
                    1:"STATUS_ERROR",
                    2:"STATUS_BUSY",
                    3:"STATUS_WAIT_CFG",
                    4:"STATUS_WAIT_INIT"} 

busy_codes = {  0:"BUSY_CODE_IDLE",
                    1:"BUSY_CODE_SELECTOR_HOMING",
                    2:"BUSY_CODE_SELECTOR_SELECTING",
                    3:"BUSY_CODE_FEED_FORWARD",
                    4:"BUSY_CODE_CUTTER_HOMING",
                    5:"BUSY_CODE_CUTTER_SELECTING",
                    6:"BUSY_CODE_EXTRUDER_FORWARD",
                    7:"BUSY_CODE_EXTRUDER_OUT_FORWARD",
                    8:"BUSY_CODE_EXTRUDER_OUT_REVERSE",
                    9:"BUSY_CODE_FEED_REVERSE",
                    10:"BUSY_CODE_FEED_REVERSE_FINAL"}    

error_codes = { 0:"ERROR_CODE_OK",
                    1:"ERROR_CODE_SELECTOR",
                    2:"ERROR_CODE_CUTTER",
                    3:"ERROR_CODE_FEED_ES",
                    4:"ERROR_CODE_EXTRUDER_ES",
                    5:"ERROR_CODE_ENGAGED",
                    6:"ERROR_CODE_DISENGAGED",
                    7:"ERROR_CODE_NO_FILAMENT",
                    8:"ERROR_CODE_NO_CUTTER",
                    9:"ERROR_CODE_FILAMENT_IN_FEED",
                    10:"ERROR_CODE_FILAMENT_IN_EX"}          

registers = {   "MB_STATE_REGISTER"                :0,
                "MB_ERROR_CODE_REGISTER"           :1,
                "MB_BUSY_CODE_REGISTER"            :2,
                "MB_CELL_0_SENSOR"                 :100,
                "MB_CELL_1_SENSOR"                 :101,
                "MB_CELL_2_SENSOR"                 :102,
                "MB_CELL_3_SENSOR"                 :103,
                "MB_CELL_4_SENSOR"                 :104,
                "MB_CELL_5_SENSOR"                 :105,
                "MB_CELL_6_SENSOR"                 :106,
                "MB_CELL_7_SENSOR"                 :107,
                "MB_PORT_IN_0_SENSOR"              :108,
                "MB_PORT_IN_1_SENSOR"              :109,
                "MB_PORT_OUT_0_SENSOR"             :110,
                "MB_PORT_OUT_1_SENSOR"             :111,
                "MB_SELECTOR_HOME_SENSOR"          :112,
                "MB_SELECTOR_CELL_POSITION"        :113,
                "MB_CUTTER_0_HOME_SENSOR"          :114,
                "MB_CUTTER_1_HOME_SENSOR"          :115,
                "MB_IS_GROUP_0_LOAD"               :1000,
                "MB_IS_GROUP_1_LOAD"               :1001,
                "MB_GROUP_0_LOAD_CELL_ID"          :1002,
                "MB_GROUP_1_LOAD_CELL_ID"          :1003,
                "MB_COMMAND_REGISTER"              :2000,
                "MB_COMMAND_PARAM_0_REGISTER"	   :2001,
                "MB_COMMAND_PARAM_1_REGISTER"	   :2002,
                "MB_COMMAND_PARAM_2_REGISTER"	   :2003,
                "MB_COMMAND_PARAM_3_REGISTER"	   :2004,
                "MB_COMMAND_PARAM_4_REGISTER"	   :2005,
                "MB_COMMAND_PARAM_5_REGISTER"	   :2006,
                "MB_RESERV"                        :5000}

# через RS485 свисток
# USB0 может меняться на USB1..3
# TODO: добавить проверку ответов модбас запросов
class ModbusManager(object):

    def __init__(self, salve_id=1, port='/dev/ttyUSB0', baudrate=115200, timeout=1, bytesize=8, stopbits=1):
        self.slave_id = salve_id
        self.client = ModbusClient(method = 'rtu', port=port, baudrate=baudrate, timeout=timeout, bytesize=bytesize, stopbits=stopbits)
        self.connection = self.connect()


    def connect(self):
        # првоеряем подключение
        connection = self.client.connect()
        while(not connection):
            connection = self.client.connect()
            print("not connected... try to connect again")
            sleep(0.5)

        print("connected succesfully")
        return connect


    def send_command(self, command: int, paarmeters: list) -> int:
        # заполняем регистры-параметры комманды
        param_index = 0
        for parameter in paarmeters:
            self.client.write_register(address=registers["MB_COMMAND_PARAM_0_REGISTER"]+param_index, value=parameter, unit=self.slave_id)
            param_index+=0

        # вызываем команду
        response = self.client.write_register(address=registers["MB_COMMAND_REGISTER"], value=command, unit=self.slave_id)
        print(response)

        return 0


    def read_state(self):
        state = self.client.read_holding_registers(registers["MB_STATE_REGISTER"], 3, unit=self.slave_id) # start_address, count, slave_id

        print("status = " + statuses[state.registers[0]])
        print("errror code = " + error_codes[state.registers[1]])
        print("busy code = " + busy_codes[state.registers[2]])

    
    def read_state_full(self):
        # отправляем запросы на данные 
        state = self.client.read_holding_registers(registers["MB_STATE_REGISTER"], 3, unit=self.slave_id) # start_address, count, slave_id
        cell_sensors = self.client.read_holding_registers(registers["MB_CELL_0_SENSOR"], 8, unit=self.slave_id) # start_address, count, slave_id
        port_in = self.client.read_holding_registers(registers["MB_PORT_IN_0_SENSOR"], 2, unit=self.slave_id) # start_address, count, slave_id
        port_out = self.client.read_holding_registers(registers["MB_PORT_OUT_0_SENSOR"], 2, unit=self.slave_id) # start_address, count, slave_id
        selector = self.client.read_holding_registers(registers["MB_SELECTOR_HOME_SENSOR"], 2, unit=self.slave_id) # start_address, count, slave_id
        cutter_home = self.client.read_holding_registers(registers["MB_CUTTER_0_HOME_SENSOR"], 2, unit=self.slave_id) # start_address, count, slave_id
        is_group_load = self.client.read_holding_registers(registers["MB_IS_GROUP_0_LOAD"], 2, unit=self.slave_id) # start_address, count, slave_id
        group_load_cell_id = self.client.read_holding_registers(registers["MB_GROUP_0_LOAD_CELL_ID"], 2, unit=self.slave_id) # start_address, count, slave_id
        group_load_cell_id = self.client.read_holding_registers(registers["MB_GROUP_0_LOAD_CELL_ID"], 2, unit=self.slave_id) # start_address, count, slave_id
        group_load_cell_id = self.client.read_holding_registers(registers["MB_GROUP_0_LOAD_CELL_ID"], 2, unit=self.slave_id) # start_address, count, slave_id
        command = self.client.read_holding_registers(registers["MB_COMMAND_REGISTER"], 1, unit=self.slave_id) # start_address, count, slave_id
        command_params = self.client.read_holding_registers(registers["MB_COMMAND_PARAM_0_REGISTER"], 6, unit=self.slave_id) # start_address, count, slave_id

        # выводим в консоль
        # статусные данные
        print("status = " + statuses[state.registers[0]])
        print("errror code = " + error_codes[state.registers[1]])
        print("busy code = " + busy_codes[state.registers[2]])

        # данные с датчиков
        print("cell sensors: " + str(cell_sensors.registers))     
        print("port in sensors: " + str(port_in.registers))        
        print("port out sensors: " + str(port_out.registers))        
        print("selector (home, cell ID): " + str(selector.registers))        
        print("cutter home: " + str(cutter_home.registers))

        # параметры загрузки 
        print("is group loaded?: " + str(is_group_load.registers))        
        print("group loaded cell ID: " + str(group_load_cell_id.registers))

        # текущая команда
        print("current command: " + str(command.registers))        
        print("current command parameters: " + str(command_params.registers))


