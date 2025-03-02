from collections import OrderedDict

class LRUCache(OrderedDict):
    def __init__(self, capacity: int):
        self.capacity = capacity
        super().__init__()
        
    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value
    
    def __setitem__(self, key, value):
        if key in self:
            self.move_to_end(key)
        super().__setitem__(key, value)
        if len(self) > self.capacity:
            removed_item = self.popitem(last=False)
            
            # Disppose removed item to free resources
            if hasattr(removed_item[1], "dispose"):
                removed_item[1].dispose()