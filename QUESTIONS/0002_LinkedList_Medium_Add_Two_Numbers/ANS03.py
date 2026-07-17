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
        head = curr = l1
        carry = 0
        prev = None
        
        while l1 and l2:
            carry += l1.val + l2.val
            l1.val = carry % 10
            carry //= 10
            prev = l1
            l1, l2 = l1.next, l2.next
            
        if l2:
            prev.next = l2
            l1 = l2
            
        while l1 and carry:
            carry += l1.val
            l1.val = carry % 10
            carry //= 10
            prev = l1
            l1 = l1.next
            
        if carry:
            prev.next = ListNode(carry)
            
        return head

