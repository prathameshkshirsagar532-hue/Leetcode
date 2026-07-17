# 1.Two_Sum
Array
level_Easy
---
Q. Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order

Example 1:

Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].
Example 2:

Input: nums = [3,2,4], target = 6
Output: [1,2]
Example 3:

Input: nums = [3,3], target = 6
Output: [0,1]
 

Constraints:

2 <= nums.length <= 104
-109 <= nums[i] <= 109
-109 <= target <= 109
Only one valid answer exists.
 

Follow-up: Can you come up with an algorithm that is less than O(n2) time complexity?

---
# sol Approach 

# 1. Two Sum

<div align="left">
  <img src="https://shields.io" alt="Topic">
  <img src="https://shields.io" alt="Difficulty">
</div>

---

### 📝 Problem Description

Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

* You may assume that each input would have **exactly one solution**.
* You may not use the same element twice.
* You can return the answer in any order.

---

### 📊 Examples

| Example | Input | Output | Explanation |
| :--- | :--- | :--- | :--- |
| **1** | `nums = [2,7,11,15]`, `target = 9` | `[0,1]` | Because `nums[0] + nums[1] == 9` |
| **2** | `nums = [3,2,4]`, `target = 6` | `[1,2]` | — |
| **3** | `nums = [3,3]`, `target = 6` | `[0,1]` | — |

---

### ⚙️ Constraints

- $2 \le \text{nums.length} \le 10^4$
- $-10^9 \le \text{nums}[i] \le 10^9$
- $-10^9 \le \text{target} \le 10^9$
- Only one valid answer exists.

>**💡 Follow-up:** Can you come up with an algorithm that is less than $\mathcal{O}(n^2)$ time complexity?

---

# 💡 Solution Approach

