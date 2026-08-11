from django.test import TestCase

# Create your tests here.
class NotesPageTest(TestCase):
    def test_notes_page_opens(self):
        response = self.client.get("/notes/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Notes Home")


class NotesDataTest(TestCase): 
    def setUp(self):
        self.normal_note = """
二次方程式とは、
ax² + bx + c = 0
の形で表される方程式である。ただし、a ≠ 0 とする。

二次方程式を解く方法には、主に以下の方法がある。

1. 因数分解
2. 平方完成
3. 解の公式

解の公式は、

x = (-b ± √(b² - 4ac)) / 2a

である。

また、

D = b² - 4ac

を判別式という。

判別式Dの値によって、実数解の個数を判断することができる。

D > 0 のとき：
異なる2つの実数解をもつ。

D = 0 のとき：
重解をもち、実数解は1つである。

D < 0 のとき：
実数解をもたない。


例：

x² - 5x + 6 = 0

を因数分解すると、

(x - 2)(x - 3) = 0

となる。

したがって、

x = 2 または x = 3

である。
"""
    #checking if note is empty
    def test_normal_note_exits(self):
        self.assertTrue(len(self.normal_note) > 0)

    #extract content from DB
        #if content of note is the same as that in DB
    
    #If TestData can be sent from the web page
    