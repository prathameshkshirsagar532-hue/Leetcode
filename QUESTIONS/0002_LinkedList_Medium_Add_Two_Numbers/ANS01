# Definition for singly-linked list.
# class ListNode(object):
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution(object):
    def addTwoNumbers(self, l1, l2):
        """
        :type l1: Optional[ListNode]
        :type l2: Optional[ListNode]
        :rtype: Optional[ListNode]
        """
        num1_str = ""
        curr1 = l1
        while curr1:
            num1_str = str(curr1.val) + num1_str
            curr1 = curr1.next
            
        num2_str = ""
        curr2 = l2
        while curr2:
            num2_str = str(curr2.val) + num2_str
            curr2 = curr2.next
            
        total_sum = int(num1_str) + int(num2_str)
        sum_str = str(total_sum)[::-1]
        
        dummy = ListNode(0)
        curr = dummy
        for char in sum_str:
            curr.next = ListNode(int(char))
            curr = curr.next
            
        return dummy.next
