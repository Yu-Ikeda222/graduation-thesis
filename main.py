import random
import numpy as np


class Student:
    def __init__(self, name, preference=[]):
        self.preference = preference
        self.preference_score_dict = {}
        self.name = name
        self.reject_count = 0
        self.score = random.sample(range(1, 100), 1)[0]
        self.matched_company = None

    def get_next_approach_company(self):
        if self.reject_count < len(self.preference):
            return self.preference[self.reject_count]
        else:
            print(self)
            return None

    # rejectしてきた企業がフェーズによっては,capacity空いてあavailableになっているのではないか
    # ここで企業のcapacity余っているかチェックかけてもいい気がしてきた、先に企業のcapacity空いてるやつを出してきて、その後で生徒でもう一回マッチングいくやつ探しにいく的な
    def delete_no_hope_to_match_company_from_preference(self, companies_list):
        # やばいこれむずい, get_unfilled_companiesとダブっている気もする
        rejected_companies = self.preference[:self.preference.index(self.matched_company.name)]
        available_rejected_companies = []
        for r_company_name in rejected_companies:
            for company in companies_list:
                if r_company_name == company.name and company.capacity != len(company.temporary_list):
                    available_rejected_companies.append(r_company_name)
        # print("ave", available_rejected_companies)
        self.preference = available_rejected_companies + self.preference[self.preference.index(self.matched_company.name):]
        new_preference_score_dict = {}
        for company in self.preference:
            new_preference_score_dict[company] = self.preference_score_dict[company]
        self.preference_score_dict = new_preference_score_dict
        # print(self.matched_company.name, self.preference_score_dict)

    # score順には並んでいない
    def re_evaluate_matched_score(self):
        plus_score = 1
        minus = np.random.normal(loc=0, scale=10, size=1)[0]
        self.preference_score_dict[self.matched_company.name] = self.preference_score_dict[
                                                                    self.matched_company.name] + plus_score + minus
        print(self.matched_company.name, self.preference_score_dict)
        self.sort_preference_by_score()

    def sort_preference_by_score(self):
        self.preference_score_dict = sorted(self.preference_score_dict.items(), key=lambda x: -x[1])
        self.preference_score_dict = fruits = dict((x, y) for x, y in self.preference_score_dict)
        print(self.preference_score_dict)


class Company:
    def __init__(self, name, capacity, preference=[]):
        self.name = name
        self.preference = preference
        self.preference_score_dict = {}
        self.capacity = capacity
        self.temporary_list = []
        self.score = random.sample(range(1, 100), 1)[0]

    def add_student_to_temporary_list(self, student):
        self.temporary_list.append(student)

    def sort_student_by_pref(self):
        # preferenceになかった時のエラーは怪しいかも
        students_list = [[student_class, priority_of_student] for student_class, priority_of_student in
                         zip(self.temporary_list, [self.preference.index(s.name) for s in self.temporary_list])]
        sorted_students_list = sorted(students_list, key=lambda x: x[1])
        self.temporary_list = [student_class for student_class, _ in sorted_students_list]

    def decide_acceptance(self, student):
        if student.name in self.preference:
            if self.capacity > len(self.temporary_list):
                self.add_student_to_temporary_list(student)
                self.sort_student_by_pref()
                return None
            elif self.preference.index(student.name) < self.preference.index(self.temporary_list[-1].name):
                rejected_student = self.temporary_list[-1]
                rejected_student.reject_count += 1
                del self.temporary_list[-1]
                return rejected_student
            else:
                rejected_student = student
                rejected_student.reject_count += 1
                return rejected_student
        else:
            rejected_student = student
            rejected_student.reject_count += 1
            return rejected_student


def DA_matching(students, companies):
    unmatched_students_list = students.copy()
    result = companies
    student_rejected_by_all_list = []
    while len(unmatched_students_list) > 0:
        # ここに全員にすでにリジェクトされてたら終わりにする的な処理を書きたい
        if unmatched_students_list[0].reject_count >= len(unmatched_students_list[0].preference):
            student_rejected_by_all_list.append(unmatched_students_list[0])
            del unmatched_students_list[0]
            continue
        company = next(
            company for company in companies if company.name == unmatched_students_list[0].get_next_approach_company())
        # next_approach_company = unmatched_students_list[0].get_next_approach_company()
        index = companies.index(company)
        outcome_of_decide = company.decide_acceptance(unmatched_students_list[0])
        # 結果的に「拒否」扱いになったstudentをunmatched_students_listに戻す
        if outcome_of_decide is None:
            unmatched_students_list[0].matched_company = company
        else:
            unmatched_students_list.append(outcome_of_decide)
        del unmatched_students_list[0]
        # 少し違和感がある
        result[index] = company
        # print(result)

    matching = {}
    for company in result:
        results = []
        for student in company.temporary_list:
            results.append(student.name)
        matching[company.name] = results
    for k, v in matching.items():
        k_score = 0
        for company in companies_list:
            if k == company.name:
                k_score = company.score
        print(k, k_score, v)
    print("rejected by all", student_rejected_by_all_list)


# preferenceのながさを先に絞っているのがどうなのか
# students_listをそのまま使うのは多分良くない、companies_list的な感じで再代入検討
def init_settings(students_list, companies_list):
    num_students = 100
    num_companies = 20
    student_preference_num = 10
    company_preference_num = 80
    capacity = 5
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
            error = np.random.normal(loc=0, scale=3, size=1)[0]
            if company.name in student.preference:
                company_priority = student.preference.index(company.name)
                biased_score = company.score + error
                student.preference[company_priority] = [student.preference[company_priority], biased_score]
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
                company.preference[student_priority] = [company.preference[student_priority], biased_score]
        sorted_students_list = sorted(company.preference, key=lambda x: -x[1])
        flat_sorted = [x for row in sorted_students_list for x in row]
        company.preference_score_dict = dict(zip(flat_sorted[0::2], flat_sorted[1::2]))
        sorted_preference_list = [company_class for company_class, _ in sorted_students_list]
        company.preference = sorted_preference_list

    # for i in range(num_students):
    #     print('学生', i + 1, 'の希望順位：', end='')
    #     print(students_list[i].preference)
    #     print()
    #
    # for i in range(num_companies):
    #     print('企業', i + 1, 'の希望順位：', end='')
    #     print(companies_list[i].preference)
    #     print()


def re_setting():
    return None


def get_unfilled_companies(companies_list):
    unfilled_list = []
    for company in companies_list:
        if len(company.temporary_list) != company.capacity:
            unfilled_list.append(company)
    return unfilled_list


def get_re_considered(students_list, companies_list):
    for student in students_list:
        # print(student.preference_score_dict)
        if student.matched_company:
            student.delete_no_hope_to_match_company_from_preference(companies_list)
            student.re_evaluate_matched_score()
        # print(student.name, student.matched_company)
        for company_name in student.preference:
            list = []
    return None


if __name__ == "__main__":
    students_list = []
    companies_list = []
    init_settings(students_list, companies_list)
    initial_students_list = students_list.copy()
    initial_company_list = companies_list.copy()
    DA_matching(students_list, companies_list)
    c_list = get_unfilled_companies(companies_list)
    print("unfilled_company", c_list)
    s_list = get_re_considered(students_list, companies_list)

    n = 3
    split_students_list = np.array_split(initial_students_list, n)
    split_companies_list = np.array_split(companies_list, n)
    # print(split_students_list)
    # print(split_companies_list)

    for i in range(n):
        students_list = split_students_list[0]
        companies_list = split_students_list[0]
