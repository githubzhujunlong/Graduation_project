import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import shutil
import os


def get_card(image, is_show):
    # 图像预处理
    car = cv.imread(image)
    if car.shape[1] > 1000:
        car = cv.resize(car, (700, 500))
    process_list = []
    process_list.append(car)

    car_gray = cv.cvtColor(car, cv.COLOR_BGR2GRAY)
    process_list.append(car_gray)

    car_blur = cv.GaussianBlur(car_gray, (23, 23), 1)
    process_list.append(car_blur)

    # 车牌定位
    x = cv.Sobel(car_blur, cv.CV_16S, 1, 0)
    y = cv.Sobel(car_blur, cv.CV_16S, 0, 1)
    Scale_AbsX = cv.convertScaleAbs(x)
    Scale_AbsY = cv.convertScaleAbs(y)
    car_Sobel = cv.addWeighted(Scale_AbsX, 0.5, Scale_AbsY, 0.5, 0)
    process_list.append(Scale_AbsX)

    ret, car_thresh = cv.threshold(Scale_AbsX, 0, 255, cv.THRESH_OTSU)
    car_thresh = cv.medianBlur(car_thresh, 9)
    process_list.append(car_thresh)

    kernel = np.ones((11, 11), np.uint8)
    car_close = cv.morphologyEx(car_thresh, cv.MORPH_CLOSE, kernel, iterations=3)
    process_list.append(car_close)

    image = cv.erode(car_close, np.ones((1, 23), np.uint8), iterations=2)
    image = cv.erode(image, np.ones((6, 1), np.uint8), iterations=2)
    image = cv.dilate(image, np.ones((13, 37), np.uint8), iterations=1)
    process_list.append(image)

    car_copy = car.copy()
    contours, hierarchy = cv.findContours(image, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cv.drawContours(car_copy, contours, -1, (0, 0, 255), 2)
    process_list.append(car_copy)

    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)
        ratio = w / h
        if ratio >= 2 and ratio <= 8:
            if x < car.shape[1] / 2 and x > car.shape[1] / 6 and y > car.shape[0] / 3:
                card_image = car[y:y + h, x:x + w]
                cv.imwrite('app/utils/card/image/card.png', card_image)
                process_list.append(card_image)
                break

    # 字符提取
    card = cv.imread('app/utils/card/image/card.png')
    image = cv.GaussianBlur(card, (3, 3), 0)
    process_list.append(image)

    image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    process_list.append(image_gray)

    ret, image_thresh = cv.threshold(image_gray, 0, 255, cv.THRESH_OTSU)
    process_list.append(image_thresh)

    area_white = 0
    area_black = 0
    h, w = image_thresh.shape
    for i in range(h):
        for j in range(w):
            if image_thresh[i, j] == 255:
                area_white += 1
            else:
                area_black += 1
    if area_white > area_black:
        ret, image_thresh = cv.threshold(image_thresh, 0, 255, cv.THRESH_OTSU | cv.THRESH_BINARY_INV)
    process_list.append(image_thresh)

    image = cv.dilate(image_thresh, np.ones((3, 2), np.uint8), iterations=1)
    process_list.append(image)

    card_copy = card.copy()
    contours, hierarchy = cv.findContours(image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cv.drawContours(card_copy, contours, -1, (0, 0, 255), 1)
    process_list.append(card_copy)

    words = []
    i = 0
    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)
        if w >= 40 or h < 20 or w <= 3:
            continue
        ratio = h / w
        if ratio > 1 and ratio <= 10:
            word = []
            word.append(x)
            word.append(y)
            word.append(w)
            word.append(h)
            words.append(word)
            i += 1

    words = sorted(words, key=lambda word: word[0])

    i = 1
    word_images = []
    shutil.rmtree('app/utils/card/image/word')
    os.mkdir('app/utils/card/image/word')
    for word in words:
        if (i > 7 and word[2] < 6) or (i == 1 and word[2] < 6):
            continue
        word_image = card[word[1]:word[1] + word[3], word[0]:word[0] + word[2]]
        word_images.append(word_image)
        cv.imwrite('app/utils/card/image/word/word_' + str(i) + '.png', word_image)
        process_list.append(word_image)
        i += 1
    shutil.rmtree('app/utils/card/image/word_thresh')
    os.mkdir('app/utils/card/image/word_thresh')
    for i in range(len(word_images)):
        word = cv.cvtColor(word_images[i], cv.COLOR_BGR2GRAY)
        ret, word = cv.threshold(word, 0, 255, cv.THRESH_OTSU | cv.THRESH_BINARY)
        #     word = cv.morphologyEx(word, cv.MORPH_OPEN, np.ones((0,0), np.uint8), iterations=1)
        word_images[i] = word
        process_list.append(word)
    for i in range(len(word_images)):
        cv.imwrite('app/utils/card/image/word_thresh/word' + str(i) + '.jpg', word_images[i])

    # 字符识别
    template = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
                'X', 'Y', 'Z',
                '藏', '川', '鄂', '甘', '赣', '贵', '桂', '黑', '沪', '吉', '冀', '津', '晋', '京', '辽', '鲁', '蒙', '闽', '宁',
                '青', '琼', '陕', '苏', '皖', '湘', '新', '渝', '豫', '粤', '云', '浙']

    def read_directory(dir):
        refer_img_list = []
        for file in os.listdir(dir):
            refer_img_list.append(dir + '/' + file)
        return refer_img_list

    def get_cn_words_list():
        cn_words_list = []
        for i in range(34, 65):
            cn_word = read_directory('app/utils/card/refer1/' + template[i])
            cn_words_list.append(cn_word)
        return cn_words_list

    cn_words_list = get_cn_words_list()

    def get_en_words_list():
        en_words_list = []
        for i in range(10, 34):
            en_word = read_directory('app/utils/card/refer1/' + template[i])
            en_words_list.append(en_word)
        return en_words_list

    en_words_list = get_en_words_list()

    def get_en_num_words_list():
        en_num_words_list = []
        for i in range(34):
            en_num_word = read_directory('app/utils/card/refer1/' + template[i])
            en_num_words_list.append(en_num_word)
        return en_num_words_list

    en_num_words_list = get_en_num_words_list()

    def template_score(template, image):
        template = cv.imdecode(np.fromfile(template, dtype=np.uint8), 1)
        template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
        ret, template = cv.threshold(template, 0, 255, cv.THRESH_OTSU)
        image_copy = image.copy()
        h, w = image_copy.shape
        template = cv.resize(template, (w, h))
        res = cv.matchTemplate(image_copy, template, cv.TM_CCOEFF)
        return res

    def template_match(word_images):
        results = []
        for index, word_image in enumerate(word_images):
            if index == 0:
                best_score = []
                for cn_words in cn_words_list:
                    all_score = []
                    for cn_word in cn_words:
                        result = template_score(cn_word, word_image)
                        all_score.append(result)
                    best_score.append(max(all_score))
                i = best_score.index(max(best_score))
                word = template[34 + i]
                results.append(word)
            elif index == 1:
                best_score = []
                for en_words in en_words_list:
                    all_score = []
                    for en_word in en_words:
                        result = template_score(en_word, word_image)
                        all_score.append(result)
                    best_score.append(max(all_score))
                i = best_score.index(max(best_score))
                word = template[10 + i]
                results.append(word)
            else:
                best_score = []
                for en_num_words in en_num_words_list:
                    all_score = []
                    for en_num_word in en_num_words:
                        result = template_score(en_num_word, word_image)
                        all_score.append(result)
                    best_score.append(max(all_score))
                i = best_score.index(max(best_score))
                word = template[i]
                results.append(word)
        return results

    res = template_match(word_images)


    def show_process(process_list):
        for p in process_list:
            cv.imshow('process', p)
            if cv.waitKey(0) & 0xFF == ord('c'):
                cv.destroyAllWindows()
                continue
            elif cv.waitKey(0) & 0xFF == ord('q'):
                break

    if is_show:
        show_process(process_list)
    return ''.join(res)


# res = get_card('image/ccc.png', True)
# print(res)
