import random
import numpy as np
import copy
import time


class Student:
    def __init__(self, name, preference=[]):
        self.preference = preference
        self.preference_score_dict = {}
        self.name = name
        self.reject_count = 0
        self.score = np.random.normal(loc=0, scale=0.5, size=1)[0]
        self.matched_company = None

    def get_next_approach_company(self):
        if self.reject_count < len(self.preference):
            return self.preference[self.reject_count]
        else:
            return None

    def delete_no_hope_to_match_company_from_preference(self, companies_list):
        # 2回目にここにきた時にmatching相手変わってなかった時抜ける
        if self.matched_company.name not in self.preference:
            return
        rejected_companies = self.preference[:self.preference.index(self.matched_company.name)]
        available_rejected_companies = []
        for r_company_name in rejected_companies:
            for company in companies_list:
                if r_company_name == company.name and company.capacity != len(company.temporary_list):
                    available_rejected_companies.append(r_company_name)
        self.preference = available_rejected_companies + self.preference[
                                                         self.preference.index(self.matched_company.name):]
        new_preference_score_dict = {}
        for company in self.preference:
            new_preference_score_dict[company] = self.preference_score_dict[company]
        self.preference_score_dict = new_preference_score_dict

    def re_evaluate_matched_score(self):
        error = np.random.normal(loc=0.1, scale=0.25, size=1)[0]
        if self.matched_company.name in self.preference_score_dict:
            self.preference_score_dict[self.matched_company.name] = self.preference_score_dict[
                                                                        self.matched_company.name] + error
        self.sort_preference_by_score()

    def sort_preference_by_score(self):
        self.preference_score_dict = sorted(self.preference_score_dict.items(), key=lambda x: -x[1])
        self.preference_score_dict = dict((x, y) for x, y in self.preference_score_dict)

    def create_new_preference(self):
        new_list = list(self.preference_score_dict.keys())
        self.preference = new_list[:new_list.index(self.matched_company.name)]


class Company:
    def __init__(self, name, capacity, preference=[]):
        self.name = name
        self.preference = preference
        self.preference_score_dict = {}
        self.capacity = capacity
        self.temporary_list = []
        self.score = np.random.normal(loc=0, scale=0.5, size=1)[0]

    def add_student_to_temporary_list(self, student):
        self.temporary_list.append(student)

    def sort_student_by_pref(self):
        students_list = [[student_class, priority_of_student] for student_class, priority_of_student in
                         zip(self.temporary_list, [self.preference.index(s.name) for s in self.temporary_list])]
        sorted_students_list = sorted(students_list, key=lambda x: x[1])
        self.temporary_list = [student_class for student_class, _ in sorted_students_list]

    def decide_acceptance(self, student):
        self.sort_student_by_pref()
        if student.name in self.preference:
            if self.capacity > len(self.temporary_list):
                if student.name not in [s.name for s in self.temporary_list]:
                    self.add_student_to_temporary_list(student)
                self.sort_student_by_pref()
                return None
            elif self.preference_score_dict[student.name] > self.preference_score_dict[self.temporary_list[-1].name]:
                self.temporary_list[-1].matched_company = None
                rejected_student = self.temporary_list[-1]
                rejected_student.reject_count += 1
                del self.temporary_list[-1]
                self.add_student_to_temporary_list(student)
                self.sort_student_by_pref()
                return rejected_student
            else:
                student.matched_company = None
                rejected_student = student
                rejected_student.reject_count += 1
                return rejected_student
        else:
            student.matched_company = None
            rejected_student = student
            rejected_student.reject_count += 1
            return rejected_student


def DA_matching(students, companies):
    unmatched_students_list = copy.deepcopy(students)
    # reject count reset
    for student in unmatched_students_list:
        student.reject_count = 0
    student_rejected_by_all_list = []
    while len(unmatched_students_list) > 0:
        # 全員にすでにリジェクトされてたら終わりにする
        if unmatched_students_list[0].reject_count >= len(unmatched_students_list[0].preference):
            student_rejected_by_all_list.append(unmatched_students_list[0])
            del unmatched_students_list[0]
            continue
        company = next(
            (company for company in companies if
             company.name == unmatched_students_list[0].get_next_approach_company()), None)
        # 自分の選好リスト上の企業が存在しないなら
        if company is None:
            unmatched_students_list[0].reject_count += 1
            student_rejected_by_all_list.append(unmatched_students_list[0])
            continue
        outcome_of_decide = company.decide_acceptance(unmatched_students_list[0])
        # 結果的に「拒否」扱いになったstudentをunmatched_students_listに戻す
        if outcome_of_decide is None:
            for student in students:
                # 内定先の企業が更新されるので、この時企業側のtemplistからこの学生を削除
                if student.name == unmatched_students_list[0].name:
                    if student.matched_company:
                        if student.matched_company.name in [company.name for company in companies]:
                            now_matched_company_index = [company.name for company in companies].index(
                                student.matched_company.name)
                            now_matched_company = companies[now_matched_company_index]
                            if student in now_matched_company.temporary_list:
                                del now_matched_company.temporary_list[
                                    now_matched_company.temporary_list.index(student)]
                    student.matched_company = company
        else:
            unmatched_students_list.append(outcome_of_decide)
        del unmatched_students_list[0]



def init_settings(students_list, companies_list):
    num_students = 500
    num_companies = 20
    student_preference_num = 20
    company_preference_num = 500
    capacity = 20
    for i in range(num_students):
        student_preference = ['c' + str(the_number_of_company) for the_number_of_company in
                              random.sample(range(1, num_companies + 1), student_preference_num)]
        student = Student('s' + str(i + 1), student_preference)
        students_list.append(student)
    for i in range(num_companies):
        company_preference = ['s' + str(the_number_of_student) for the_number_of_student in
                              random.sample(range(1, num_students + 1), company_preference_num)]
        company = Company('c' + str(i + 1), capacity, company_preference)
        companies_list.append(company)

    for student in students_list:
        for company in companies_list:
            error = np.random.normal(loc=0, scale=0.25, size=1)[0]
            if company.name in student.preference:
                company_priority = student.preference.index(company.name)
                biased_score = company.score + error
                if biased_score > 0:
                    student.preference[company_priority] = [student.preference[company_priority], biased_score]
                else:
                    del student.preference[company_priority]
        sorted_companies_list = sorted(student.preference, key=lambda x: -x[1])
        flat_sorted = [x for row in sorted_companies_list for x in row]
        student.preference_score_dict = dict(zip(flat_sorted[0::2], flat_sorted[1::2]))
        sorted_preference_list = [company_class for company_class, _ in sorted_companies_list]
        student.preference = sorted_preference_list

    for company in companies_list:
        for student in students_list:
            error = np.random.normal(loc=0, scale=3, size=1)[0]
            if student.name in company.preference:
                student_priority = company.preference.index(student.name)
                biased_score = student.score + error
                if biased_score > 0:
                    company.preference[student_priority] = [company.preference[student_priority], biased_score]
                else:
                    del company.preference[student_priority]
        sorted_students_list = sorted(company.preference, key=lambda x: -x[1])
        flat_sorted = [x for row in sorted_students_list for x in row]
        company.preference_score_dict = dict(zip(flat_sorted[0::2], flat_sorted[1::2]))
        sorted_preference_list = [company_class for company_class, _ in sorted_students_list]
        company.preference = sorted_preference_list



def get_unfilled_companies(companies_list):
    unfilled_list = []
    for company in companies_list:
        if len(company.temporary_list) != company.capacity:
            unfilled_list.append(company)
    return unfilled_list


def get_unmatched_students(students_list):
    unfilled_list = []
    for student in students_list:
        if student.matched_company is None:
            unfilled_list.append(student)
    return unfilled_list


def get_re_considered(students_list, companies_list):
    re_match_students = []
    for student in students_list:
        if student.matched_company:
            student.delete_no_hope_to_match_company_from_preference(companies_list)
            student.re_evaluate_matched_score()
            student.create_new_preference()
            if len(student.preference) > 0:
                re_match_students.append(student)
        else:
            re_match_students.append(student)
    return re_match_students


def normal_DA(students_list, companies_list):
    DA_matching(students_list, companies_list)
    # for company in companies_list:
    #     print(company.name)
    #     for s in company.temporary_list:
    #         print(s.name, company.preference_score_dict[s.name])

    # path = 'outputs/normal_DA.txt'
    # f = open(path, 'w')
    # for company in companies_list:
    #     f = open(path, 'a')
    #     f.write(company.name)
    #     f.write(' ')
    #     f.write(str(company.score))
    #     f.write('\n')
    #     for matched_student in company.temporary_list:
    #         f.write(matched_student.name)
    #         f.write(' ')
    #     f.write('\n')
    #     f.close()


def divided_DA(students_list, companies_list):
    n = 3
    split_students_list = np.array_split(students_list, n)
    split_companies_list = np.array_split(companies_list, n)

    re_match_students = []
    re_match_companies = []
    last_student_matching = []
    last_company_matching = []

    for i in range(n):
        matching_students_list = split_students_list[i].tolist() + re_match_students
        matching_companies_list = split_companies_list[i].tolist() + re_match_companies

        DA_matching(matching_students_list, matching_companies_list)
        last_company_matching += matching_companies_list
        last_student_matching += matching_students_list
        c_list = get_unfilled_companies(matching_companies_list)
        re_match_companies = c_list

        s_list = get_unmatched_students(matching_students_list)
        re_match_students = s_list

    companies = []
    students = []
    for company in last_company_matching:
        if company.capacity > len(company.temporary_list):
            companies.append(company)

    for student in last_student_matching:
        if student.matched_company is None:
            students.append(student)

    DA_matching(students, companies)


def divided_rejoin_DA(students_list, companies_list):
    n = 3
    split_students_list = np.array_split(students_list, n)
    split_companies_list = np.array_split(companies_list, n)

    re_match_students = []
    re_match_companies = []
    last_student_matching = []
    last_company_matching = []

    for i in range(n):
        matching_students_list = split_students_list[i].tolist() + re_match_students
        matching_companies_list = split_companies_list[i].tolist() + re_match_companies

        DA_matching(matching_students_list, matching_companies_list)
        last_company_matching += matching_companies_list
        last_student_matching += matching_students_list
        c_list = get_unfilled_companies(matching_companies_list)
        re_match_companies = c_list

        s_list = get_re_considered(matching_students_list, matching_companies_list)
        re_match_students = s_list

    companies = []
    students = []
    for company in last_company_matching:
        if company.capacity > len(company.temporary_list):
            companies.append(company)

    for student in last_student_matching:
        if student.matched_company is None:
            students.append(student)

    DA_matching(students, companies)

    # path = 'outputs/divided_rejoin_DA.txt'
    # f = open(path, 'w')
    # for company in companies_list:
    #     f = open(path, 'a')
    #     f.write(company.name)
    #     f.write(' ')
    #     f.write(str(company.score))
    #     f.write('\n')
    #     for matched_student in company.temporary_list:
    #         f.write(matched_student.name)
    #         f.write(' ')
    #     f.write('\n')


def duration_DA(students_list, companies_list):
    n = 3
    split_students_list = np.array_split(students_list, n)
    split_companies_list = np.array_split(companies_list, n)
    for i in range(n):
        DA_matching(split_students_list[i].tolist(), split_companies_list[i].tolist())


def count_blocking_pair(students, companies):
    num_blocking_pair = 0
    for student in students:
        possible_pair = []
        if student.matched_company and student.matched_company.name in student.preference:
            # 期を跨いでいたらない可能性がある
            possible_pair_name = student.preference[:student.preference.index(student.matched_company.name)]
            # print(student.matched_company.name)
        else:
            possible_pair_name = student.preference
        # print(possible_pair_name)
        for c_name in possible_pair_name:
            for company in companies:
                if c_name == company.name:
                    possible_pair.append(company)
        # print(possible_pair)
        for c in possible_pair:
            if student.name in c.preference_score_dict:
                if len(c.temporary_list) == 0:
                    num_blocking_pair += 1
                elif c.preference_score_dict[student.name] > c.preference_score_dict[c.temporary_list[-1].name]:
                    # print(student.name,c.name, c.preference_score_dict[student.name], c.temporary_list[-1].name,c.preference_score_dict[c.temporary_list[-1].name])
                    # for s in c.temporary_list:
                        # print(c.name, student.name, c.preference_score_dict[student.name], s.name,c.preference_score_dict[s.name])
                    # print(c.name, student.name,c.preference_score_dict[student.name], c.temporary_list[-1].name, c.temporary_list[-1].score )
                    num_blocking_pair += 1
            break
    return num_blocking_pair


# def count_blocking_pair(students1, companies1, students2, companies2):
#     s_num_block = 0
#     for student in students2:
#         matched_company = student.matched_company
#         if matched_company:
#             possible_company = None
#             for company in companies1:
#                 if company.name == matched_company.name:
#                     possible_company = company
#             # print(possible_company.preference_score_dict)
#             for s in possible_company.temporary_list:
#                 if possible_company.preference_score_dict[s.name] < possible_company.preference_score_dict[
#                     student.name]:
#                     # print(s.name, student.name)
#                     s_num_block += 1
#                     break
#         else:
#             possible_student = None
#             for s in students1:
#                 if student.name == s.name:
#                     possible_student = s
#             if possible_student is not None and possible_student.matched_company is not None:
#                 s_num_block += 1
#     c_block_num = 0
#     for company in companies2:
#         matched_students = company.temporary_list
#         if len(matched_students) > 0:
#             for student in students1:
#                 for m_student in matched_students:
#                     if student.name == m_student.name:
#                         possible_student = student
#                         if possible_student.matched_company is not None and company.name in possible_student.preference:
#                             if possible_student.preference_score_dict[possible_student.matched_company.name] < possible_student.preference_score_dict[company.name]:
#                                 c_block_num += 1
#                 break
#         else:
#             possible_company = None
#             for c in companies1:
#                 if company.name == c.name:
#                     possible_company = c
#             if possible_company is not None and len(possible_company.temporary_list) > 0:
#                 c_block_num += 1
#
#     return np.array([s_num_block, c_block_num])


def calculate_utility(students, companies):
    u_students = 0
    for s in students:
        if s.matched_company:
            u_students += s.preference_score_dict[s.matched_company.name]
    u_companies = 0
    for c in companies:
        if len(c.temporary_list) > 0:
            u_companies += sum([c.preference_score_dict[s.name] for s in c.temporary_list])
    u_students = u_students / len(students)
    u_companies = u_companies / len(companies)
    return np.array([u_students, u_companies], dtype=float)


def analyze(students1, companies1, students2, companies2):
    students1_score = []
    students2_score = []
    companies1_score = []
    companies2_score = []
    for student in students1:
        if student.matched_company:
            students1_score.append(student.preference_score_dict[student.matched_company.name])
        else:
            students1_score.append(0)
    for student in students2:
        if student.matched_company:
            students2_score.append(student.preference_score_dict[student.matched_company.name])
        else:
            students2_score.append(0)
    for company in companies1:
        company_score = 0
        for s in company.temporary_list:
            company_score += company.preference_score_dict[s.name]
        companies1_score.append(company_score)
    for company in companies2:
        company_score = 0
        for s in company.temporary_list:
            company_score += company.preference_score_dict[s.name]
        companies2_score.append(company_score)
    np_students1 = np.array(students1_score)
    np_students2 = np.array(students2_score)
    np_student_error = np_students1 - np_students2
    np_companies1 = np.array(companies1_score)
    np_companies2 = np.array(companies2_score)
    np_company_error = np_companies1 - np_companies2
    # minusは後ろの方が優れてる、plusは前の方が優れてる、つまりminusが少ない方が優れている
    # {"students": [minus, plus], "companies": [minus, plus]}
    result = np.array([[len(np_student_error[np_student_error < 0]), len(np_student_error[np_student_error > 0])],
                       [len(np_company_error[np_company_error < 0]), len(np_company_error[np_company_error > 0])]])
    return result


if __name__ == "__main__":
    t1 = time.time()

    u_one = np.array([0, 0], dtype=float)
    u_two = np.array([0, 0], dtype=float)
    u_three = np.array([0, 0], dtype=float)
    u_four = np.array([0, 0], dtype=float)

    # {"students": [minus, plus], "companies": [minus, plus]}
    one_minus_two = np.array([[0, 0], [0, 0]])
    one_minus_three = np.array([[0, 0], [0, 0]])
    one_minus_four = np.array([[0, 0], [0, 0]])
    two_minus_three = np.array([[0, 0], [0, 0]])
    two_minus_four = np.array([[0, 0], [0, 0]])
    three_minus_four = np.array([[0, 0], [0, 0]])

    blocking_one = 0
    blocking_two = 0
    blocking_three = 0
    blocking_four = 0

    n = 1000
    for i in range(n):
        students_list = []
        companies_list = []
        init_settings(students_list, companies_list)
        initial_students_list = copy.deepcopy(students_list)
        initial_company_list = copy.deepcopy(companies_list)
        initial1_students_list = copy.deepcopy(students_list)
        initial1_company_list = copy.deepcopy(companies_list)
        initial2_students_list = copy.deepcopy(students_list)
        initial2_company_list = copy.deepcopy(companies_list)
        initial3_students_list = copy.deepcopy(students_list)
        initial3_company_list = copy.deepcopy(companies_list)
        initial4_students_list = copy.deepcopy(students_list)
        initial4_company_list = copy.deepcopy(companies_list)

        # print("1 start normal DA")
        normal_DA(initial1_students_list, initial1_company_list)
        print()
        # print("2 start divided rejoin DA")
        divided_rejoin_DA(initial2_students_list, initial2_company_list)
        print()
        # print("3 start divided DA")
        divided_DA(initial3_students_list, initial3_company_list)
        print()
        # print("4 start duration DA")
        duration_DA(initial4_students_list, initial4_company_list)

        u_one += calculate_utility(initial1_students_list, initial1_company_list)
        u_two += calculate_utility(initial2_students_list, initial2_company_list)
        u_three += calculate_utility(initial3_students_list, initial3_company_list)
        u_four += calculate_utility(initial4_students_list, initial4_company_list)

        one_minus_two += analyze(initial1_students_list, initial1_company_list, initial2_students_list,
                                 initial2_company_list)
        one_minus_three += analyze(initial1_students_list, initial1_company_list, initial3_students_list,
                                   initial3_company_list)
        one_minus_four += analyze(initial1_students_list, initial1_company_list, initial4_students_list,
                                  initial4_company_list)
        two_minus_three += analyze(initial2_students_list, initial2_company_list, initial3_students_list,
                                   initial3_company_list)
        two_minus_four += analyze(initial2_students_list, initial2_company_list, initial4_students_list,
                                  initial4_company_list)
        three_minus_four += analyze(initial3_students_list, initial3_company_list, initial4_students_list,
                                    initial4_company_list)

        blocking_one += count_blocking_pair(initial1_students_list, initial1_company_list)
        blocking_two += count_blocking_pair(initial2_students_list, initial2_company_list)
        blocking_three += count_blocking_pair(initial3_students_list, initial3_company_list)
        blocking_four += count_blocking_pair(initial4_students_list, initial4_company_list)


    u_one = u_one / n
    u_two = u_two / n
    u_three = u_three / n
    u_four = u_four / n

    one_minus_two = one_minus_two / n
    one_minus_three = one_minus_three / n
    one_minus_four = one_minus_four / n
    two_minus_three = two_minus_three / n
    two_minus_four = two_minus_four / n
    three_minus_four = three_minus_four / n

    blocking_one = blocking_one / n
    blocking_two = blocking_two / n
    blocking_three = blocking_three / n
    blocking_four = blocking_four / n

    print(u_one)
    print(u_two)
    print(u_three)
    print(u_four)

    print('{"students": [minus, plus], "companies": [minus, plus]}')
    print("1-2", one_minus_two)
    print("1-3", one_minus_three)
    print("1-4", one_minus_four)
    print("2-3", two_minus_three)
    print("2-4", two_minus_four)
    print("3-4", three_minus_four)
    print("blocking pair", blocking_one, blocking_two, blocking_three, blocking_four)

    t2 = time.time()
    elapsed_time = t2 - t1
    print(f"経過時間：{elapsed_time}")
