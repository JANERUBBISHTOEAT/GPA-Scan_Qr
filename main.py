import cv2 as cv
from pyzbar import pyzbar as pyzbar
from os.path import dirname, join

# Constants
REPEATED  = "REPEATED"
APPROVED  = "APPROVED"
NOT_FOUND = "NOT FOUND"
_ENCODING = "utf-8"
VERSION   = str(hex(20200409))


# Global Var
prev_Data = ""
code_List = []
name_List = []
scanned = []
cnt = 0
status = ""

def open_record():
    
    global cnt
    global scanned
    global code_List
    global name_List
    # print(sys.getdefaultencoding())

    print("----------------------------")
    print("Reading records from res.txt:")
    
    try: 
        fp = open(join(dirname(__file__),"res.txt"), mode = 'r', encoding = _ENCODING)
    except:
        print("[ERROR] Cannot find file: "+ join(dirname(__file__),"res.txt"))
        input("")
        return False
    # "Check#Code#Name"
    text = fp.read()
    # print(text)
    for line in text.split('\n'):
        if '#' in line:
            scanned.append(line.split('#')[0])
            code_List.append(line.split('#')[1])
            name_List.append(line.split('#')[2].rstrip('\n'))
            if (scanned[cnt]):
                print("|-√- " + name_List[cnt])
            else:
                print("|--- " + name_List[cnt])
            cnt += 1
        else:
            print("Unexpected Format Detected")
    fp.close()
    print("Record read sucesfully.")
    print("-----------------------\n")
    return True


def mark_as_attend(barcodeData):

    global cnt
    global scanned
    global code_List
    global name_List

    if (barcodeData in code_List):
        if (scanned[code_List.index(barcodeData)] == "CHECK"):
            print("[WARNING] Repeated Comfirmation: \"{}\"\n".format(name_List[code_List.index(barcodeData)]))
            # messagebox.showinfo("WARNING", "Repeated Comfirmation: \"" + barcodeData + "\"")
            return REPEATED
        else:
            print("[√] Marking \"{}\" as attended".format(barcodeData))
            print("Welcome, {}!\n".format(name_List[code_List.index(barcodeData)]))
            scanned[code_List.index(barcodeData)] = "CHECK"
            fp = open(join(dirname(__file__),"res.txt"), mode = 'w', encoding = _ENCODING) # rerwite res.
            for i in range(cnt):
                fp.write(scanned[i] + '#' + code_List[i] + '#' + name_List[i] + '\n')
                # print("Writing information: {}, {}".format(cnt, scanned[i] + '#' + name_List[i]))
            fp.close()
            return APPROVED

    else:
        print("[ERROR] !!! Name: \"{}\" not found!!!\n".format(barcodeData))
        # messagebox.showerror("ERROR", "Name: \"" + barcodeData + "\" not found!!!")
        return NOT_FOUND


def decodeDisplay(image):

    global status # for cv status display
    global prev_Data

    barcodes = pyzbar.decode(image)

    for barcode in barcodes:
        # 提取二维码的边界框的位置
        # 画出图像中条形码的边界框
        (x, y, w, h) = barcode.rect

        # color in BGR
        color = (255, 255, 255)
        if (status == APPROVED):
            color = (0, 255, 0) # Green
        elif (status == REPEATED):
            color = (0, 255, 255) # Yellow
        elif (status == NOT_FOUND):
            color = (0, 0, 255) # Red
        else:
            color = (142, 142, 142) # Gery

        cv.rectangle(image, (x, y), (x + w, y + h), color, 2)

        # 提取二维码数据为字节对象，所以如果我们想在输出图像上
        # 画出来，就需要先将它转换成字符串
        barcodeData = barcode.data.decode("UTF8")
        barcodeType = barcode.type

        # 绘出图像上条形码的数据和条形码类型
        # text = "{} ({})".format(barcodeData, barcodeType)
        cv.putText(image, status, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX,.5, color, 2)
        # 向终端打印条形码数据和条形码类型
        if (barcodeData != prev_Data):
            print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
            prev_Data = barcodeData
            status = mark_as_attend(barcodeData)

    return image


def detect():
    # camera = cv.VideoCapture(0) # Choose camera here
    camera_index = int(input("Index of camera: "))
    camera = cv.VideoCapture(camera_index, cv.CAP_DSHOW) # Speed up
    
    while True:
        # 读取当前帧
        ret, frame = camera.read()
        # 转为灰度图像
        # Turn background to grey
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        gray = cv.cvtColor(gray, cv.COLOR_GRAY2BGR)

        im = decodeDisplay(gray)

        c=cv.waitKey(5)#等待5毫秒
        cv.imshow("camera" + str(camera_index), im)
        if(c==27):#按下esc键关闭摄像头窗口
            camera.release()
            cv.destroyAllWindows()
            break

if __name__ == '__main__':
    print("Running on ver." + VERSION[2:])
    if (open_record()):
        detect()