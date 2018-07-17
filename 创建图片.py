from PIL import Image,ImageDraw,ImageFont

# 创建图片
img = Image.new(mode="RGB",size=(120,30),color=(255,255,20))

# 创简笔画，用于在图片上画任意内容
# img = Image.new(mode="RGB",size=(120,30),color=(255,255,20))
draw = ImageDraw.Draw(img, mode="RGB")

# 画点
# img = Image.new(mode="RGB",size=(120,30),color=(25
#
# ]5,255,20))
# draw = ImageDraw.Draw(img, mode="RGB")
# 第一个参数表示坐标，第二个fill的参数表示颜色
draw.point([100,100],fill="red")
draw.point([300,300],fill=(255,255,0))

# 画圆
# img = Image.new(mode="RGB",size=(120,30),color=(255,255,20))
# draw = ImageDraw.Draw(img, mode="RGB")
# 第一个参数：表示起始坐标
# 第二个参数：表示写入的内容能够
# 第三个参数：表示颜色
draw.text([0,0],"python","red")

# 特殊字体文字
img = Image.new(mode='RGB', size=(120, 30), color=(255, 255, 255))
draw = ImageDraw.Draw(img, mode='RGB')
# 第一个参数：表示字体文件路径
# 第二个参数：表示字体大小
font = ImageFont.truetype("kumo.ttf", 28)
# 第一个参数：表示起始坐标
# 第二个参数：表示写入内容
# 第三个参数：表示颜色
# 第四个参数：表示颜色
# 在图片查看器中打开
img.show()

# 保存在本地
with open("code.png","wb")as f:
    img.save(f,format="png")
