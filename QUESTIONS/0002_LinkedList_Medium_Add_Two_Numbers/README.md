# 0002. Add Two Numbers

### 🏷️ Question Overview
* **Topic:** `LinkedList`
* **Difficulty:** `Medium`
* **LeetCode Link:** [Add Two Numbers](https://leetcode.com)

---

### 📝 Problem Statement
You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list.

You may assume the two numbers do not contain any leading zero, except the number 0 itself.

---

### 🎨 Visual Flow (Example 1)

```text
[List 1]     (2) ——> (4) ——> (3)     =  342
              +       +       +
[List 2]     (5) ——> (6) ——> (4)     =  465
              │       │       │
[Carry]       0       1       0      (Addition Carry)
              ▼       ▼       ▼
[Result]     (7) ——> (0) ——> (8)     =  807
```

---

### 📥 Test Cases

#### **Example 1**
* **Input:** `l1 = [2,4,3]`, `l2 = [5,6,4]`
* **Output:** `[7,0,8]`
* **Explanation:** `342 + 465 = 807`

#### **Example 2**
* **Input:** `l1 = [0]`, `l2 = [0]`
* **Output:** `[0]`

#### **Example 3**
* **Input:** `l1 = [9,9,9,9,9,9,9]`, `l2 = [9,9,9,9]`
* **Output:** `[8,9,9,9,0,0,0,1]`

---

### ⚙️ Constraints
* The number of nodes in each linked list is in the range `[1, 100]`.
* `0 <= Node.val <= 9`
* It is guaranteed that the list represents a number that does not have leading zeros.




### Soln approach through proceess
# 📔 DOCUMENTARY: LeetCode 2 (Add Two Numbers) - Mera Thinking Log
> **Focus:** Maine kaise socha, kya doubts aaye, aur unhe kaise samjha.

---

## 1. MERE SHURUAT KE THOUGHTS & INTEGER OVERFLOW
* **Mene Pehle Kya Socha:** Dono arrays/lists ko ulta (reverse) karo -> Phir unhe number me convert karke plus (+) kar do -> Phir jo answer aaye uski wapas list bana do.
* **Problem Kya Mili:** Agar LeetCode ne bohot badi list de di (jaise 100 digits lamba number), toh jab use number me badlenge toh computer ki memory limit cross ho jayegi, jisse **Integer Overflow** ho jayega.
* **Mera Pivot:** Mujhe number me bina convert kiye, jaise school me ek-ek digit karke normal maths me plus karte hain, waise hi add karna padega.

---

## 2. REVERSE KARNE KA REALIZATION
* **Mene Socha Tha:** Kya aakhri me answer list ko ulta (reverse) karna padega?
* **Concept Clarity:** Nahi! Kyunki inputs pehle se hi ulte order me diye hain (jaise 342 hume `2 -> 4 -> 3` mila hai). Maths me bhi hum piche se hi jorna shuru karte hain, aur humara pehla node hi sabse piche waala digit hai. Toh agar hum seedha-seedha jodte jayenge, toh answer bhi automatically ulta (sahi order me) banta chala jayega. No list reversal needed!

---

## 3. MERA SABSE BADA DOUBT: POINTER KAISE KAAM KARTA HAI?
* **Mera Doubt:** "Agar mene code me likha `l1.val`, toh computer ko kaise pata chalega ki main konse node par hu? Loop aage kaise badh raha hai?"
* **Maine Kya Sikha:** `l1` koi fixed data variable nahi hai, wo ek **Pointer** hai. Wo sirf memory me us node ka pata (address) yaad rakhta hai jahan wo abhi khada hai.
* **Pointer Movement:** Computer tab tak usi same node par ruka rahega jab tak hum use khud aage nahi badhayenge. Agar hum loop ke andar:
  ```python
  l1 = l1.next
  ```
  nahi likhenge, toh pointer wahi phasa rahega aur **Infinite Loop** ban jayega. Yeh line likhne se hi pointer agle node par koodta hai.

---

## 4. HANDLING MISMATCHED LENGTHS (SAFE CODING)
* **Problem Kya Thi:** Agar ek number 3-digit ka hai aur dusra 5-digit ka, toh choti list pehle khatam ho jayegi aur `l1` ki value `None` ho jayegi. Agar mene galti se `None.val` likh diya, toh code crash ho jayega.
* **Maine Kaise Samjha:** Loop ke andar ek safe check lagana padega. Agar list bachi hai toh uski real value uthao aur pointer aage badhao, nahi toh uski value ko `0` maan lo taaki code crash na ho:
  ```python
  val1 = l1.val if l1 else 0
  l1 = l1.next if l1 else None
  ```

---

## 5. CARRY NIKALNE KE LIYE MATH OPERATORS
Agar do digits ko jor kar `12` aata hai, toh mujhe `2` ko node me dalna hai aur `1` ko carry banana hai. Iske liye do operators zaroori hain:
* **Modulo (`% 10`):** Yeh hume naya digit nikal kar dega (`12 % 10 = 2`).
* **Floor Division (`// 10`):** Yeh hume carry nikal kar dega (`12 // 10 = 1`).

---

## 6. FINAL BLUEPRINT
Mera while loop tab tak chalega jab tak dono me se kisi ek list me data bacha ho, YA aakhri me koi carry bacha ho:
```python
while l1 or l2 or carry:
    # 1. l1 aur l2 se safely values nikalna (agar khatam toh 0 maanna)
    # 2. Sum nikalna, aur % aur // use karke digit aur carry nikalna
    # 3. Pointers ko safely aage badhana
```


## new Soln jo mene samja or sikha kese socha ja sakta hai
