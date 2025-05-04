class FunctionExpression:
    
    def __init__(self, name, col, distinct=False):
        self.name = name
        self.col = col
        self.distinct = distinct
        self.parent = col.parent if hasattr(col, 'parent') else None
    
    def __str__(self):
        if not self.col:
            return f"{self.name}()"

        if self.distinct:
            return f"DISTINCT {self.col}"

        return f"{self.name}({self.col})"


class Function:
    
    def distinct(self, column):
        return FunctionExpression(None, column, distinct=True)
    
    def __getattr__(self, name):
        def function_generator(col):
            return FunctionExpression(name.upper(), col)
        return function_generator


func = Function()
