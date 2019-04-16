"""
Chú thích: 1 dãy mua hàng dạng <{20, 40}{30}{20}{10, 30}>: gọi là 1 giao dịch
              {20, 60}, {40},... gọi là 1 lần mua hàng
              10, 20,... gọi là 1 sản phẩm
"""
import copy
import re

def readInput():
    # Reading Sequence file
    S = []
    Slines = []
    temp_1 = []
    with open('data.txt', 'rt') as Sfile:
        for line in Sfile:
            #đọc từng dòng, loại bỏ dấu \n cuối dòng và thêm vào tạo thành 1 list
            Slines.append(line.rstrip('\n'))
        for line in Slines:
            #bỏ 2 dấu ngoặc nhọn 2 bên
            line = line.strip()[1:-1]
            #tách các giao dịch trong 1 dòng ra thành các giao dịch con dạng list
            for s in re.split(r'}{', line[1:-1]):
                temp = [int(i) for i in re.split(', ', s)]
                #temp1 là list của các list gd dạng: [[10, 40, 50], [40, 90]], [[20, 30]...
                temp_1.append(temp)
            S.append(temp_1)
            temp_1 = []
    #S = [[[10, 40, 50], [40, 90]], [[20, 30], [70, 80], [20, 30, 70]], [[10, 40], [40]]]........

    # Đọc file chứa danh sách các sản phẩm
    with open('para.txt', 'r') as file:
        listProc = [int(line) for line in file.read().split(',')]
        listProc.sort()
    return S, listProc

def MsGsp(S, listProc, MIS):
    CountMap = {}
    # Số lượng chuỗi giao dich
    seqCount = len(S)

    for i in listProc:
        # Đếm số giao dịch của 1 sản phẩm
        count = 0
        # Duyệt qua giao dịch của mỗi người
        for row in S:
            # Duyệt qua từng lần mua hàng
            for elem in row:
                if (i in elem):
                    count = count + 1
                    # Dict chứa tên sp mà số lần được mua(1 giao dịch chỉ tính 1 lần)
                    CountMap[i] = count
                    break

    # List các sản phẩm + số lần xuất hiện thỏa mãn minSup
    #  [[10, 3], [20, 5], [30, 4], [40, 3], [50, 3], [60, 2]]
    L = init_pass(listProc, CountMap,seqCount, MIS)

    #list các sản phẩm thỏa mãn minSup
    F1 = [i[0] for i in L]

    #ghi kết quả vào file theo format
    output_file = open("Output_GSP.txt", "w")
    output_file.write("The number of length 1 sequential pattern is " + str(len(F1)) + "\n")
    for f in F1:
        print_s = "Pattern : <{" + str(f) + "}"
        print_s += ">"
        print_s += ": Count = " + str(CountMap[f])
        output_file.write(print_s + "\n")

    k = 2
    while (True):
        if k == 2:
            # Tập ứng viên có 2 phần tử
            Ck = level_2(L)
        else:
            # Tập ứng viên có > 2 phần tử
            Ck = MScandidateGen(Fk)

        # Đếm số lần xuất hiện và so sánh với minSup
        # Lưu tần số xuất hiện của các phần tử trong C
        SupCount = [0] * len(Ck)
        for c in range(len(Ck)):
            temp_count = 0
            for s in S:
                # đếm số giao dịch có chứa Ck
                if Sub(Ck[c], s):
                    temp_count += 1
            SupCount[c] = temp_count
        # List chứa các chuỗi thỏa mãn minSup
        Fk = []
        # List chứa các chuỗi + số lần xuất hiện thỏa mãn minSup
        Fk_withcount = []
        for c in range(len(Ck)):
            if SupCount[c] / seqCount >= 0.4:
                Fk.append(Ck[c])
                Fk_withcount.append([Ck[c], SupCount[c]])
        if (len(Fk) == 0):
            break

        #ghi ra file theo format
        output_file.write("The number of length: " + str(k) + " sequential pattern is " + str(len(Fk)) + "\n")
        for f in Fk_withcount:
            print_s = "Pattern : <"
            for s in f[0]:
                print_s += "{"
                for i in s:
                    print_s += str(i) + ","
                print_s = print_s[:-1]
                print_s += "}"
            print_s += ">:Count = " + str(f[1])
            output_file.write(print_s + "\n")
        k += 1

# kiểm tra xem s có chứa Ck không
# Ck là 1 sản phẩm trong C
# s là 1 lần mua hàng
def Subset(Ck, s):
    for i in Ck:
        if i not in s:
            return False
    return True

# s là 1 chuỗi giao dich của 1 người
# Kiểm tra xem Ck có trong chuỗi giao dịch s không
def Sub(Ck, s):
    m = {}
    # Biến đếm để đảm bảo thứ tự mua hàng
    counter = 0
    for i in Ck:
        isThere = False
        j = counter
        while j < len(s):
            # Tìm xem MỖI LẦN mua hàng có sản phẩm i hay không (xét từng cụm trong 1 giao dịch)
            # s[j] là mỗi lần mua hàng.[[20, 40], [30], [20]] =>3 lần mua hàng
            if Subset(i, s[j]):
                m[j] = True
                isThere = True
                counter = j + 1
                break
            j += 1
        if not isThere:
            # Nếu 1 sản phầm trong C không có thì return False luôn
            return False
    return True


# Trả về F1 có dạng [[10, 3], [20, 5],...]
def init_pass(M, CountMap, seqCount, MIS):
    LMap = {}
    for i in M:
        support = float(CountMap[i]) / float(seqCount)
        if (support >= MIS):
            LMap[i] = CountMap[i]
    add_to_L = [[k, v] for k, v in LMap.items()]
    return add_to_L


# Tổ hợp của của dãy có 2 sản phầm( trong 1 lần mua + 2 lần mua)
def level_2(L):
    C2 = []
    for i in range(0, len(L)):
        #2 sản phẩm giống nhau trong 2 lần mua
        C2.append([[L[i][0]], [L[i][0]]])
        for j in range(i + 1, len(L)):
            if L[i][0] < L[j][0]:
                #2 sản phẩm khác nhau trong 1 lần mua
                C2.append([[L[i][0], L[j][0]]])
            else:
                C2.append([[L[j][0], L[i][0]]])
            #2 sản phẩm khác nhau trong 2 lần mua và đảo thứ tự
            C2.append([[L[i][0]], [L[j][0]]])
            C2.append([[L[j][0]], [L[i][0]]])
    return C2


def MScandidateGen(F):
    # F <class 'list'>: [[[10], [10]], [[10], [20]], [[20], [10]], [[30], [10]], [[40], [10]],...]
    C = []
    for i in F:
        for j in F:
            s1 = i
            s2 = j
            #removeItem(s1, 0): list sau khi xóa sản phẩm đầu tiên của s1
            #removeItem(s2, Length(s2) - 1): list sau khi xóa sản phẩm đầu tiên s2
            #s1: <class 'list'>: [[20], [20], [30]] -> [[20], [30]]
            #s2: <class 'list'>: [[20], [30, 50]] -> [[20], [30]]
            if (removeItem(s1, 0) == removeItem(s2, Length(s2) - 1)):
                # Nếu chiều dài của phần tử cuối cùng trong s2 bằng 1 thì thêm nó vào c1
                if (len(s2[-1]) == 1):
                    # dùng s1.copy() để khi thêm phần tử vào c1 thì s1 không bị thay đổi
                    c1 = s1.copy()
                    c1.append(s2[-1])
                    C.append(c1)
                else:
                # Thay đổi phần tử cuối cùng của c1 bằng phần tử cuối cùng của s2
                    c1 = s1.copy()
                    del (c1[-1])
                    c1.append(s2[-1])
                    C.append(c1)
    return C


def removeItem(s, index):
    # Dùng deepcopy để khi thay đổi giá trị của seqnew thì s không thay đổi
    seqnew = copy.deepcopy(s)
    count = 0
    for element in seqnew:
        if count + len(element) <= index:
            count += len(element)
        else:
            # Xóa đi 1 sản phẩm tùy thuộc vào index(đầu - cuối)
            # Xóa đầu: <class 'list'>: [[20, 40], [20], [30]] => [[40], [20], [30]]
            # Xóa cuối: <class 'list'>: [[20], [30, 50]] => [[20], [30]]
            del element[index - count]
            break
    # Trả về danh sách sản phẩm sau khi xóa để so sánh
    return [element for element in seqnew if len(element) > 0]


def Length(s):
    l = 0
    for i in s:
        l += len(i)
    return l


if __name__ == '__main__':
    S, listProc = readInput()
    MIS = 0.4
    MsGsp(S, listProc, MIS)