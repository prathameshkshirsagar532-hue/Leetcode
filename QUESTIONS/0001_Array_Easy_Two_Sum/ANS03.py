class Solution(object):
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        seen={}
        for i in range(len(nums)):
            complement=target-nums[i]
            if complement in seen:
                return[i,seen[complement]]
            seen[nums[i]]=i
        return []
