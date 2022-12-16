import random

# 学生の数
S = 10

# 企業の数
C = 4

s_pref_num = 2
s_pref = [random.sample(range(1, C + 1), s_pref_num) for i in range(S)]
# print(s_pref)
for i in range(S):
    print('学生', i + 1, 'の希望順位：', end='')
    for j in range(s_pref_num):
        print(' c{0}'.format(s_pref[i][j]), end='')
    print()
print()

c_pref = [random.sample(range(1, S + 1), S) for i in range(C)]
for i in range(C):
    print('企業', i + 1, 'の希望順位：', end='')
    for j in range(S):
        print(' s{0}'.format(c_pref[i][j]), end='')
    print()
print()

# 企業の希望順位を左からs1の順位，s2の順位，……に変換する
capacity_of_one_company = 10
c_order = [[0] * S for i in range(C)]
for i in range(C):
    for j in range(capacity_of_one_company):
        k = c_pref[i][j]
        c_order[i][k - 1] = j + 1

print("変換後c_order", c_order)
# 企業の定員
capacity = [2] * 4

# マッチした相手
s_matched = [0] * (S + 1)
c_matched = [[0] * (S + 1) for i in range(C)]
print()

# 仮マッチしている学生の数
num_match = 0

# 学生に仮マッチした相手がいれば1，そうでなければ0
s_filled = [0] * (S + 1)

# 企業の定員が埋まっていれば1，そうでなければ0？？
c_filled = [0] * C

# 第何希望まですでにプロポーズしたか
position = [0] * (S + 1)

print('camacity', capacity)
print('c_matched', c_matched)

# ステップ数
t = 1
while num_match < S:
    print('ステップ {}'.format(t))
    for i in range(S):
        # 学生に仮マッチした相手がいな時
        if s_filled[i] == 0:
            # 学生がプロポーズする相手
            print('s_pref', s_pref)
            index_company_proposed = s_pref[i][position[i]] - 1
            print()
            print('s{0}がc{1}にプロポーズ'.format(i + 1, index_company_proposed + 1))
            # 企業の定員に空きがある場合
            # s_pref[i][position[i]]が相手を指しているけど、それをあわらすのが配列的には-1
            # print("c_filled c_filled[j] capacity[j]", c_filled, c_filled[j], capacity[j])
            if c_filled[index_company_proposed] < capacity[index_company_proposed]:  # これおかしくないか
                # iとindex_company_proposedがマッチ
                c_matched[index_company_proposed][i] = 1
                s_matched[i] = index_company_proposed
                print('　s{0}とc{1}が仮マッチ'.format(i + 1, index_company_proposed + 1))
                print(c_matched)
                print(s_matched)
                s_filled[i] = 1
                c_filled[index_company_proposed] += 1
                num_match += 1
            # 企業の定員がすでに埋まっている場合
            else:
                temp = -1
                # ダミープレーヤー
                rejected = S
                for k in range(S):
                    if c_matched[index_company_proposed][k] == 1:
                        # 学生kがリジェクトされる候補になるなら
                        if c_order[index_company_proposed][i] < c_order[index_company_proposed][k] and c_order[index_company_proposed][k] > temp:
                            # 前に仮リジェクトされた学生を戻す
                            s_filled[rejected] = 1
                            position[rejected] -= 1
                            c_matched[index_company_proposed][rejected] = 1
                            s_matched[rejected] = j
                            # 新たに学生kを仮リジェクトする
                            s_filled[k] = 0
                            position[k] += 1
                            rejected = k
                            c_matched[index_company_proposed][k] = 0
                            temp = c_pref[index_company_proposed][k]
                            print('　c{0}がs{1}をリジェクト'.format(index_company_proposed + 1, k + 1))

                # 学生iが企業index_company_proposedに受け入れられたならば
                if temp > -1:
                    c_matched[index_company_proposed][i] = 1
                    s_matched[i] = index_company_proposed
                    print('　s{0}とc{1}が仮マッチ'.format(i + 1, index_company_proposed + 1))
                    s_filled[i] = 1
                else:
                    print('　c{0}がs{1}をリジェクト'.format(index_company_proposed + 1, i + 1))
                    position[i] += 1
                    # すべての企業にプロポーズしたらアンマッチ
                    if position[i] == C:
                        s_matched[i] = -1
                        s_filled[i] = 1
                        num_match += 1
            print()
    t += 1
    print()

# 　マッチング結果の印字
print('マッチング結果')
for i in range(S):
    if s_matched[i] == -1:
        print('s{0}:'.format(i + 1))
    else:
        print('s{0}: c{1}'.format(i + 1, s_matched[i] + 1))

for j in range(C):
    if c_filled[j] == 0:
        print('  : c{0}'.format(j + 1))



# print(students_list)
        # student_name_list = [s.name for s in self.temporary_list]
        # print("pre",self.preference)
        # print("ord", student_name_list)
        # order_of_student_name = sorted(student_name_list, key=self.preference.index)
        # print("order", order_of_student_name)

        # print(l)
        # # ['Banana', 'Alice', 'Apple', 'Bob']
        #
        # print([l_order.index(s) for s in l])
        # # [3, 0, 2, 1]
        #
        # print(sorted(l, key=l_order.index))
        # # ['Alice', 'Bob', 'Apple', 'Banana']

        # for s in self.temporary_list:
        #     priority_of_student = self.preference.index(s.name)
        #     self.temporary_list.remove(s)
        #     self.temporary_list.insert(priority_of_student, )
        # print("順番", [self.preference.index(s) for s in [s.name for s in self.temporary_list]])
        # print(self.temporary_list)
        # print("ここをクラスにしたい", sorted([s.name for s in self.temporary_list], key=self.preference.index))
        # self.temporary_list = sorted(self.temporary_list, key=lambda student: sorted(student.name, key=self.preference.index))
        # self.temporary_list = sorted(self.temporary_list, key=self.preference.index)



# student_preference = ['c' + str(the_number_of_company) for the_number_of_company in random.sample(range(1, num_companies + 1), student_preference_num)]
# student = Student('s' + str(i+1), student_preference)

    # for student in students_list:
        # for company in companies_list:
        #     error_term = np.random.normal(loc=0, scale=3, size=1)[0]
        #     student.score = student.score + error_term
        #     company.preference.append([student.name, student.score])
        #     company_preference = [['s' + str(the_number_of_student)] for the_number_of_student in random.sample(range(1, num_companies + 1), company_preference_num)]
        #     student_preference = ['c' + str(the_number_of_company) for the_number_of_company in random.sample(range(1, num_companies + 1), student_preference_num)]
    # for company in companies_list:
    #     error_term = np.random.normal(loc=0, scale=3, size=1)[0]
    #     company.score = company.score + error_term
    #     student.preference.append([company.name, company.score])