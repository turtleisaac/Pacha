class Buffer:
    def __init__(self, data, *args, write=False):
        self.data = data
        self.pos = 0
        self.write = write

    def read_u8(self):
        if self.pos <= len(self.data):
            ret = self.data[self.pos] & 0xff
            self.pos += 1
            return ret
        else:
            raise Exception('Past end of bytearray')

    def read_u16(self):
        if self.pos + 2 <= len(self.data):
            u8_1 = self.read_u8()
            u8_2 = self.read_u8() << 8
            ret = u8_2 | u8_1
            # Don't need to increment self.pos because it is handled by read_u8()
            return ret
        else:
            print(self.data[self.pos:])
            raise Exception('Past end of bytearray: position ' + str(self.pos) + ' out of ' + str(len(self.data)) +
                            ' on attempted read of 2')

    def read_u32(self):
        if self.pos + 4 <= len(self.data):
            u16_1 = self.read_u16()
            u16_2 = self.read_u16() << 16
            ret = u16_2 | u16_1
            # Don't need to increment self.pos because it is handled by read_u16()
            return ret
        else:
            print(self.data[self.pos:])
            raise Exception('Past end of bytearray: position ' + str(self.pos) + ' out of ' + str(len(self.data)) +
                            ' on attempted read of 4')

    def read_u64(self):
        if self.pos + 8 <= len(self.data):
            u32_1 = self.read_u32()
            u32_2 = self.read_u32() << 32
            ret = u32_2 | u32_1
            # Don't need to increment self.pos because it is handled by read_u32()
            return ret
        else:
            raise Exception('Past end of bytearray')

    def read_bytes(self, read_length):
        if self.pos + read_length <= len(self.data):
            ret = self.data[self.pos:self.pos + read_length]
            self.pos += read_length
            return ret
        else:
            raise Exception('Past end of bytearray')

    def seek_local(self, val):
        if self.pos + val < len(self.data):
            self.pos += val
        else:
            raise Exception('Past end of bytearray')

    def seek_global(self, offset):
        if offset < len(self.data):
            self.pos = offset
        else:
            raise Exception('Past end of bytearray')

    def toggle_write(self, state):
        self.write = state

    def write_u8(self, val):
        if self.pos < len(self.data) and self.write:
            self.data[self.pos] = val & 0xff
            self.pos += 1
        elif self.pos >= len(self.data) and self.write:
            raise Exception('Past end of bytearray')
        else:
            raise Exception('Write not enabled')

    def write_u16(self, val):
        if self.pos + 2 <= len(self.data) and self.write:
            u8_1 = val & 0xff
            u8_2 = (val >> 8) & 0xff
            self.write_u8(u8_1)
            self.write_u8(u8_2)
        elif self.pos >= len(self.data) and self.write:
            raise Exception('Past end of bytearray')
        elif self.pos + 2 >= len(self.data) and self.write:
            raise Exception('Write will go past end of bytearray')
        else:
            raise Exception('Write not enabled')

    def write_u32(self, val):
        if self.pos + 4 <= len(self.data) and self.write:
            u16_1 = val & 0xffff
            u16_2 = (val >> 16) & 0xffff
            self.write_u16(u16_1)
            self.write_u16(u16_2)
        elif self.pos >= len(self.data) and self.write:
            raise Exception('Past end of bytearray')
        elif self.pos + 4 >= len(self.data) and self.write:
            raise Exception('Write will go past end of bytearray')
        else:
            raise Exception('Write not enabled')

    def write_u64(self, val):
        if self.pos + 8 <= len(self.data) and self.write:
            u32_1 = val & 0xffffffff
            u32_2 = (val >> 32) & 0xffffffff
            self.write_u16(u32_1)
            self.write_u16(u32_2)
        elif self.pos >= len(self.data) and self.write:
            raise Exception('Past end of bytearray')
        elif self.pos + 8 >= len(self.data) and self.write:
            raise Exception('Write will go past end of bytearray')
        else:
            raise Exception('Write not enabled')

    def write_bytes(self, arr):
        if self.pos <= len(self.data) and self.pos + len(arr) <= len(self.data):
            for x in arr:
                self.write_u8(x)
        elif self.pos >= len(self.data) and self.write:
            raise Exception('Past end of bytearray')
        elif self.pos + len(arr) >= len(self.data) and self.write:
            raise Exception('Write will go past end of bytearray')
        else:
            raise Exception('Write not enabled')

    def __len__(self):
        return len(self.data)
