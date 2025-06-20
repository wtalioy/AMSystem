from app.dbrm import Table

class FunctionExpression:
    
    def __init__(self, name, col=None, *args, distinct=False):
        self.name = name
        self.col = col
        self.args = args
        self.distinct = distinct
        self.parent = col.parent if hasattr(col, 'parent') else None
    
    def __str__(self):
        if not self.col and not self.args:
            return f"{self.name}()"

        if self.distinct:
            return f"DISTINCT {self.col}"
            
        # Handle multiple arguments for functions like CONCAT, EXTRACT, etc.
        if self.args:
            all_args = [str(self.col)] if self.col else []
            all_args.extend([str(arg) for arg in self.args])
            return f"{self.name}({', '.join(all_args)})"

        return f"{self.name}({self.col})"


class DateExtractExpression(FunctionExpression):
    """Special expression for EXTRACT function"""
    
    def __init__(self, part, column):
        self.part = part
        self.column = column
        super().__init__("EXTRACT")
    
    def __str__(self):
        if hasattr(self.column, 'parent') and hasattr(self.column, 'name') and self.column.parent is not None:
            column_str = f"{self.column.parent.__tablename__}.{self.column.name}"
        else:
            column_str = str(self.column)
        return f"EXTRACT({self.part} FROM {column_str})"


class DateFormatExpression(FunctionExpression):
    """Special expression for DATE_FORMAT function"""
    
    def __init__(self, column, format_str):
        self.column = column
        self.format_str = format_str
        super().__init__("DATE_FORMAT")
    
    def __str__(self):
        if hasattr(self.column, 'parent') and hasattr(self.column, 'name') and self.column.parent is not None:
            column_str = f"{self.column.parent.__tablename__}.{self.column.name}"
        else:
            column_str = str(self.column)
        return f"DATE_FORMAT({column_str}, '{self.format_str}')"


class ConcatExpression(FunctionExpression):
    """Special expression for CONCAT function"""
    
    def __init__(self, *args):
        self.concat_args = args
        super().__init__("CONCAT")
    
    def __str__(self):
        formatted_args = []
        for arg in self.concat_args:
            if hasattr(arg, 'parent') and hasattr(arg, 'name') and arg.parent is not None:
                # It's a column with a valid parent
                formatted_args.append(f"{arg.parent.__tablename__}.{arg.name}")
            elif isinstance(arg, (FunctionExpression, DateExtractExpression, ArithmeticExpression, CeilExpression)):
                # It's another function or arithmetic expression
                formatted_args.append(str(arg))
            elif isinstance(arg, str):
                # It's a string literal
                formatted_args.append(f"'{arg}'")
            else:
                # Other values
                formatted_args.append(str(arg))
        return f"CONCAT({', '.join(formatted_args)})"


class CeilExpression(FunctionExpression):
    """Special expression for CEIL/CEILING function"""
    
    def __init__(self, expression):
        self.expression = expression
        super().__init__("CEILING")
    
    def __str__(self):
        return f"CEILING({self.expression})"


class ArithmeticExpression:
    """Expression for arithmetic operations like column / value"""
    
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __str__(self):
        left_str = str(self.left)
        right_str = str(self.right)
        return f"({left_str} {self.operator} {right_str})"
    
    def __truediv__(self, other):
        """Support for / operator"""
        return ArithmeticExpression(self, '/', other)
    
    def __mul__(self, other):
        """Support for * operator"""
        return ArithmeticExpression(self, '*', other)
    
    def __add__(self, other):
        """Support for + operator"""
        return ArithmeticExpression(self, '+', other)
    
    def __sub__(self, other):
        """Support for - operator"""
        return ArithmeticExpression(self, '-', other)


class Function:
    
    def distinct(self, column):
        return FunctionExpression(None, column, distinct=True)
    
    def extract(self, part, column):
        """Extract date part: func.extract('year', column)"""
        return DateExtractExpression(part.upper(), column)
    
    def date_format(self, column, format_str):
        """Format date: func.date_format(column, '%Y-%m')"""
        return DateFormatExpression(column, format_str)
    
    def concat(self, *args):
        """Concatenate values: func.concat(arg1, arg2, ...)"""
        return ConcatExpression(*args)
    
    def ceil(self, expression):
        """Ceiling function: func.ceil(expression)"""
        return CeilExpression(expression)
        
    def ceiling(self, expression):
        """Alias for ceil"""
        return self.ceil(expression)
    
    def arithmetic(self, left, operator, right):
        """Create arithmetic expression: func.arithmetic(column, '/', 3)"""
        return ArithmeticExpression(left, operator, right)
    
    def __getattr__(self, name):
        def function_generator(col, *args):
            if args:
                return FunctionExpression(name.upper(), col, *args)
            else:
                return FunctionExpression(name.upper(), col)
        return function_generator


func = Function()
