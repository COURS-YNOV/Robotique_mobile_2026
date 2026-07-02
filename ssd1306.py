from micropython import const
import framebuf
class SSD1306_I2C(framebuf.FrameBuffer):
 def __init__(self,w,h,i2c,addr=0x3c):
  self.w=w; self.h=h; self.i2c=i2c; self.addr=addr; self.pages=h//8
  self.buffer=bytearray(self.pages*w); super().__init__(self.buffer,w,h,framebuf.MONO_VLSB)
  for c in (0xae,0x20,0x00,0x40,0xa1,0xa8,h-1,0xc8,0xd3,0x00,0xda,0x12,0xd5,0x80,0xd9,0xf1,0xdb,0x30,0x81,0xff,0xa4,0xa6,0x8d,0x14,0xaf): self.cmd(c)
  self.fill(0); self.show()
 def cmd(self,c): self.i2c.writeto(self.addr,bytes((0x80,c)))
 def show(self):
  for c in (0x21,0,self.w-1,0x22,0,self.pages-1): self.cmd(c)
  self.i2c.writeto(self.addr,b'\x40'+self.buffer)
