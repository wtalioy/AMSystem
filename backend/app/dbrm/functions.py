class FunctionExpression:
    
    def __init__(self, name, *args, distinct=False):
        self.name = name
        self.args = args
        self.distinct = distinct
    
    def __str__(self):
        if not self.args:
            return f"{self.name}()"
            
        if self.distinct and len(self.args) == 1:
            return f"DISTINCT {self.args[0]}"
        else:
            args_str = ", ".join(str(arg) for arg in self.args)
            
        return f"{self.name}({args_str})"


class Function:
    
    def distinct(self, column):
        return FunctionExpression(None, column, distinct=True)
    
    def __getattr__(self, name):
        def function_generator(*args):
            return FunctionExpression(name.upper(), *args)
        return function_generator


func = Function()
