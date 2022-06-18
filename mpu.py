from machine import Pin,I2C


MPU_ADDR = 0x68

REG_MNG_SLEEP = 0x6B

REG_ACCEL_HIGH = 0x3F
REG_ACCEL_LOW = 0x40

REG_ACCEL_CONFIG = 0x1C

ACCEL_SCALE_2G = 16384.0
ACCEL_SCALE_4G = 8192.0
ACCEL_SCALE_8G = 4096.0
ACCEL_SCALE_16G = 2048.0

ACCEL_RANGE_2G = 0x00
ACCEL_RANGE_4G = 0x08
ACCEL_RANGE_8G = 0x10
ACCEL_RANGE_16G = 0x18

class MPU6050:
    
    def __init__(self,scl_pin,sda_pin,_range):
        self.i2c = I2C(scl=Pin(scl_pin),sda=Pin(sda_pin))
        print(self.i2c.scan())
        self.range = _range
        self.i2c.writeto_mem(MPU_ADDR, REG_MNG_SLEEP, bytes([0]))
        self.i2c.writeto_mem(MPU_ADDR, REG_ACCEL_CONFIG, bytes([self.range]))
        
    def combine_reg(self,high, low):
        if not high[0] & 0x80:
            return (high[0] << 8) | low[0]
        return -((high[0] ^ 255) << 8) | (low[0] ^ 255) + 1
    
    
    def scale_z_value(self,z):
        accel_range  = self.i2c.readfrom_mem(MPU_ADDR, REG_ACCEL_CONFIG, 1)
        if accel_range == ACCEL_RANGE_2G:
            return z / ACCEL_SCALE_2G
        elif accel_range == ACCEL_RANGE_4G:
            return z / ACCEL_SCALE_4G
        elif accel_range == ACCEL_RANGE_8G:
            return z / ACCEL_SCALE_8G
        elif accel_range == ACCEL_RANGE_16G:
            return z / ACCEL_SCALE_16G
        return z / ACCEL_SCALE_2G
    
    def get_accel_z_value(self,g = True):
        z_h = self.i2c.readfrom_mem(MPU_ADDR, REG_ACCEL_HIGH, 1)
        z_l = self.i2c.readfrom_mem(MPU_ADDR, REG_ACCEL_LOW, 1)
        
        z = self.combine_reg(z_h, z_l)
        
        z = self.scale_z_value(z)
            
        if g is False:
            return z * 9.80665
        return z
    
    

