Two_Sum
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

109 <= nums[i] <= 109

109 <= target <= 109

Only one valid answer exists.
 

Follow-up: Can you come up with an algorithm that is less than O(n2) time complexity?

---

## soln approach 

mene iskon pehle brutal tarikhe se solve kiya ho ek maths logical or simple hai jesa sab soche hai Aap log mene ans 1 ko dekh sakte jo ANS01 file hai or uska thoda implemented virson ANS02 me hai or then mene uska new tarikha sikha with help of Google serch ka Ai se vo mera teacher hi ek tarikhe se ek dam perfect or sahi Tarah se guide karta hai nahi sirf answer deta hai vo muje meri thinking karne me help karta hai or problem ko kis Tarah se samja ja sakta hai vo muje batata hai or samjata hai or usko apne tarikhe se khud se naye tarikhe se answer ko coach kar or new logic ke  sath new code or logic ko sikhte hai fir mene apnin puri Tarah se koshis ke bad fir muje vo correct approach or sahi tarikha ya fast tarikha ya kuch nahi method sikha deta hai  and is soln me kuch ese chijo ke bare me likhunga jo muje is questions ko samjene me or solve karne me Meri thinking level ko badhane me help karegi

## ek kahani jo is questions ko solve karne me help karkegi refer solN ANS03 or ANS04

🕵️‍♂️ **Ek Mast Real-Life Example (Chor aur Police)**  
Maano ek party chal rahi hai aur wahan bohot saare log khade hain. Aap ek detective ho. Aapka target hai ek aise do logo ki jodi ko dhoondhna jinake paas maujood paise milakar 10 ho jayein (Target = 10).

**Purana Tarika (Aapka do loops wala code):**  
Aap pehle aadmi ke paas gaye, uske paas 3 rupaye the. Ab aap baki party me khade ek-ek aadmi ke paas jaakar puch rahe ho—"Kya tere paas 7 rupaye hain? Kya tere paas 7 rupaye hain?" Yeh karne me bohot time lagta hai kyunki aapko har baar puri bheed me ghumna padta hai (O(n²) mehnat).

**Naya aur Fast Tarika (Sirf Ek Loop):**  
Is baar aapne dimaag lagaya. Aapne gate par ek Register (Diary) rakh di. Aap line se sabko ek-ek karke bula rahe ho: Pehla aadmi aaya, uske paas 3 rupaye hain. Aapne socha: "Mujhe total 10 chahiye, toh mujhe 7 rupaye wale ki zaroorat hai." Aapne apni Register me dekha, kya wahan pehle se koi 7 rupaye wala likha hai? Nahi! Toh aapne is 3 rupaye wale ka naam aur uski position apni Register me note kar li aur use party me bhej diya. Doosra aadmi aaya, uske paas 4 rupaye hain. Aapne socha: "Mujhe 6 rupaye wale ki zaroorat hai." Register check kiya... wahan 6 nahi hai. Aapne 4 rupaye wale ko bhi Register me likh liya. Teesra aadmi aaya, uske paas 7 rupaye hain! Aapne socha: "Mujhe 3 rupaye wale ki zaroorat hai." Jaise hi aapne apni Register me dekha... BINGO! Wahan pehle se hi 3 rupaye wale ka naam aur uski position likhi hui thi! Aapne turant wahi par bol diya—"Mil gayi jodi! Yeh teesra aadmi aur Register me likha pehla aadmi, dono milkar 10 banate hain."

**Is Kahani Se Hame Kya Seekha?**  
Is tarike me aapko bheed me baar-baar ghumna nahi pada (yaani doosra loop nahi chalana pada). Aapne bas ek-ek karke sabko dekha, aur jo nahi mila use Register me likhte gaye. Coding ki duniya me is "Register" ko hum Hash Map ya Python me Dictionary ({}) kehte hain. Agar hum is tarike se code likhein, toh poori list par sirf ek hi loop chalega. Time Complexity O(n²) se ghatkar sirf O(n) ho jayegi, yaani aapka code super-fast chalega!

**Ab Aap Kya Karna Chahte Hain?**  
Agar aapko yeh Register wala logic samajh aaya ho, toh batayein: Kya aap Python me Dictionary ({}) use karke iska logic khud se try karna chahte hain? (Main aapko coding me help karunga) Ya aap abhi kisi naye problem / question par jana chahte hain? Mujhe batayein, hum waise hi aage badhenge!

