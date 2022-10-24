import numpy as np, cv2

def onMouse(event, x, y, flags, param): # 마우스 이벤트 함수, 드래그하여 원하는 부분을 선택
    global mouse_point, start_y, start_x, select_image_size,finish_x, finish_y, Exit_drag

    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_point = True
        start_x = x
        start_y = y

    elif event == cv2.EVENT_MOUSEMOVE:
        if mouse_point == True:
            image2 = image.copy()
            cv2.rectangle(image2, (start_x, start_y), (x,y), (0,0,255))
            cv2.imshow('image', image2)

    elif event == cv2.EVENT_LBUTTONUP:
        mouse_point = False
        finish_x = x
        finish_y = y
        if(start_x < finish_x and start_y > finish_y): #오른쪽 위로 드래그
            temp = start_y
            start_y = finish_y
            finish_y = temp
        elif(start_x > finish_x and start_y < finish_y): #왼쪽 밑으로 드래그
            temp = start_x
            start_x = finish_x
            finish_x = temp
        elif(start_x > finish_x and start_y > finish_y): #왼쪽 위로 드래그
            temp1, temp2 = start_x, start_y
            start_x, start_y = finish_x, finish_y
            finish_x, finish_y = temp1, temp2

        select_image = image[start_y:finish_y, start_x:finish_x]
        cv2.imwrite('select_image.jpg',select_image)

    elif event == cv2.EVENT_RBUTTONDOWN:
        Exit_drag = False

def mosaic(image): #선택 부분에 대한 이미지를 받음
    dst = image.copy()
    db, dg, dr = cv2.split(dst) #컬러 이미지를 split하여 b,g,r부분을 따로 나눔
    dst_list = []
    dst_list.append(db), dst_list.append(dg), dst_list.append(dr) #b,g,r부분에 블러를 반복문을 통해 코드 길이를 절약할 것이기 때문에 리스트로 저장

    row, col = image.shape[0], image.shape[1]
    row = int(row / 12) * 12 - 12 #10x10크기의 격자를 만들어야하기 때문에 선택한 이미지의 크기가 10의 배수가 아닐 경우 나머지버림
    col = int(col / 12) * 12 - 12

    for k in range(3):  #b,g,r부분을 따로 블러처리하기 위한 반복
        t_dst = dst_list[k]
        for i in range(0, col, 12): #한 격자를 연산하고, 겹치지 않고 다음 엑셀에 접근하기 위해 10씩 건너뜀
            for j in range(0, row, 12):
                pixel = 0.0
                for x in range(12):
                    for y in range(12):
                        pixel += t_dst[j + y, i + x]  #10x10크기의 격자의 픽셀값들을 모두 더함
                        t_dst[j:j + y, i:i + x] = int(pixel / 144) #더한 픽셀값의 평균을 삽입


        dst_list[k] = t_dst
    dst = cv2.merge([dst_list[0], dst_list[1], dst_list[2]]) #따로 블러링을 하고 나중에 다시 합쳐서 컬러이미지로 만듬
    return dst

# 블러링을 여러번 한 방식
# def blur_filter(image,mask): #선택 부분에 대한 이미지를 받음
#     dst = image.copy()
#     db, dg, dr = cv2.split(dst) #컬러 이미지를 split하여 b,g,r부분을 따로 나눔
#     dst_list = []
#     dst_list.append(db), dst_list.append(dg), dst_list.append(dr) #b,g,r부분에 블러를 반복문을 통해 코드 길이를 절약할 것이기 때문에 리스트로 저장
#
#     row, col = np.arange(1, image.shape[0] - 1), np.arange(1, image.shape[1] - 1)
#
#     for k in range(3):  #b,g,r부분을 따로 블러처리하기 위한 반복
#         t_dst = dst_list[k]
#         for i in range(15): #한 번에 블러처리는 이미지 식별이 쉽기 때문에 여러번 블러링
#             for i in col:
#                 for j in row:
#                     pixel = 0.0
#                     for x in range(mask.shape[0]):
#                         for y in range(mask.shape[1]):
#                             pixel += mask[x, y] * t_dst[j + y - 1, i + x - 1]
#
#                     t_dst[j, i] = pixel
#             dst_list[k] = t_dst
#     dst = cv2.merge([dst_list[0], dst_list[1], dst_list[2]]) #따로 블러링을 하고 나중에 다시 합쳐서 컬러이미지로 만듬
#     return dst

def change_image(image, blur_image): #블러링이 된 선택부분을 원본 이미지 부분과 교체
    dst = image.copy()
    db, dg, dr = cv2.split(dst)     #b,g,r을 나눠 따로 교체 후 합치기 위함
    dst_list = []
    dst_list.append(db), dst_list.append(dg), dst_list.append(dr)

    b, g, r = cv2.split(blur_image)
    bgr = []
    bgr.append(b), bgr.append(g), bgr.append(r)
    zero_image = np.zeros(db.shape[:2], np.uint8)

    for i in range(3):
        t_dst = dst_list[i]
        t_bgr = bgr[i]

        t_dst[start_y:finish_y, start_x:finish_x] = 0  #이미지에서 내가 선택한 부분을 0으로 함
        zero_image[start_y:finish_y ,start_x:finish_x] = t_bgr #원본 이미지와 같은 크기의 제로 이미지에 선택한 부분만 블러이미지를 넣음
        dst2 = cv2.add(t_dst, zero_image)

        dst_list[i] = dst2

    dst = cv2.merge([dst_list[0], dst_list[1], dst_list[2]])
    return dst

mouse_point = False
Exit_drag = True
start_x, start_y = -1,-1
finish_x, finish_y = -1,-1

# 블러링 방식을 이용할때 사용
# data = [1/9, 1/9, 1/9, 1/9, 1/9, 1/9, 1/9, 1/9, 1/9]
# mask = np.array(data).reshape(3, 3)

capture = cv2.VideoCapture(0)
ret, frame = capture.read()
cv2.imwrite('image.jpg', frame)
image=cv2.imread('image.jpg',cv2.IMREAD_COLOR)
cv2.imshow("image", image)
origin_image = image.copy()

while(True):
    cv2.setMouseCallback("image", onMouse, image)
    cv2.waitKey(0)
    select_image = cv2.imread("select_image.jpg", cv2.IMREAD_COLOR)
    mosaic_image = mosaic(select_image)
    #blur_image = blur_filter(select_image,mask) #블러링 방식
    mosaic_image = np.array(mosaic_image, dtype='uint8')
    image = change_image(image, mosaic_image)

    if Exit_drag == False:
        break

cv2.imshow("origin_image", origin_image)
cv2.imshow("mosaic_image", image)
cv2.waitKey(0)
capture.release()
cv2.destroyAllWindows()