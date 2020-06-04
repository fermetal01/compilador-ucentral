from compiler.core.Number import Number
from compiler.core.Token import Token
from compiler.core.error.RTError import RTError
from compiler.core.util.RTResult import RTResult


class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    ###################################

    def visit_NumberNode(self, node, context):
        return RTResult().success(
            Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"'{var_name}' is not defined",
                context
            ))

        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error: return res

        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error: return res
        right = res.register(self.visit(node.right_node, context))
        if res.error: return res

        if node.op_tok.type == Token.TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == Token.TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == Token.TT_MUL:
            result, error = left.multiplied_by(right)
        elif node.op_tok.type == Token.TT_DIV:
            result, error = left.dived_by(right)
        elif node.op_tok.type == Token.TT_POW:
            result, error = left.powed_by(right)
        elif node.op_tok.type == Token.TT_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == Token.TT_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_tok.type == Token.TT_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == Token.TT_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == Token.TT_LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_tok.type == Token.TT_GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_tok.matches(Token.TT_KEYWORD, 'AND'):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(Token.TT_KEYWORD, 'OR'):
            result, error = left.ored_by(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res

        error = None

        if node.op_tok.type == Token.TT_MINUS:
            number, error = number.multiplied_by(Number(-1))
        elif node.op_tok.matches(Token.TT_KEYWORD, 'NOT'):
            number, error = number.notted()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))
