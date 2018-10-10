from cobra.warningLog import Warning

# add_check = []
# assertions = []

warning = []


def check_num_overflow(node):
    # warning = []
    ass = []
    add_check = []
    mul_check = []
    sp_add_check = []
    sp_mul_check = []
    check_overflow(node, ass, add_check, mul_check, sp_add_check, sp_mul_check)
    if len(add_check) > 0:
        for a in add_check:
            if str(a[0] + "=" + a[1] + "+" + a[2]) not in warning:
                warning.append(str(a[0] + "=" + a[1] + "+" + a[2]))
                # print("The add operation might overflow! start: ", a[3])
    if len(mul_check) > 0:
        for a in mul_check:
            if str(a[0] + "=" + a[1] + "*" + a[2]) not in warning:
                warning.append(str(a[0] + "=" + a[1] + "*" + a[2]))
                # print("The multiplication operation might overflow! start: ", a[3])
    if len(sp_add_check) > 0:
        for a in sp_add_check:
            if str(a[0] + "+=" + a[1]) not in warning:
                warning.append(str(a[0] + "+=" + a[1]))
                # print("The add operation might overflow! start: ", a[3])
    if len(sp_mul_check) > 0:
        for a in sp_mul_check:
            if str(a[0] + "*=" + a[1]) not in warning:
                warning.append(str(a[0] + "*=" + a[1]))
                # print("The multiplication operation might overflow! start: ", a[3])
    return warning


def check_overflow(node, ass, add_check, mul_check, sp_add_check, sp_mul_check):
    if isinstance(node, list):
        for n in node:
            check_overflow(n, ass, add_check, mul_check, sp_add_check, sp_mul_check)
        return
    elif isinstance(node, dict):
        if node["type"] == "AssignmentExpression" and node["operator"] in ("+=", "*=", "-="):
            # print("OOOOOOOOOOOOOOOOOOOKKKKKKKKKKKKKKKKKKK")
            left, right = check_left_right_expression(node)
            # print(left)
            # print(right)
            if left and right:
                if node["operator"] == "+=" and str(left + "+=" + right) not in warning:
                    sp_add_check.append((left, right))
                    # print("SSSSSSSTRANGE!!!!!!!" + str(len(sp_add_check)) + left + right)
                    # print("HHHAAAAAAA+=")
                    # print(left)
                    # print(right)
                elif node["operator"] == "*=" and str(left + "*=" + right) not in warning:
                    sp_mul_check.append((left, right))
                elif node["operator"] == "-=" and str(left + "-=" + right) not in warning:
                    if (right, left) not in ass:
                        warning.append(str(left + "-=" + right))
            # elif left is None and right:
            #     new_left = check_left_identifier(node)
            #     new_right = check_left_identifier(node)
            #     print("OOOOOOOOOOOOAAAAAAAAAAAA" + new_left)
            #     print("OOOOOOOOOOOOAAAAAAAAAAAA" + new_right)
            #     sp_add_check.append((new_left, right))
            # elif right is None and left:
            #     new_right = check_right_identifier(node)

            # elif expression["operator"] == "-=":
            #     arg = (right, left)  # (b, a)
            #     # print("PODSDJSDHJSHDSDJDSH" + str(left + "-" + right))
            #     # check if assert function has been used for the subtraction op
            #     if arg not in ass and str(node["left"]["name"] + "=" + left + "-" + right) not in warning:
            #         # print("!!!!!!!!!!!!!!!!" + node["left"]["name"])
            #         # print("???????????????????????????????" + str(left + "-" + right))
            #         warning.append(str(node["left"]["name"] + "=" + left + "-" + right))
            # print("Find possible subtraction operation overflow at [", expression["start"],
            #       expression["end"], "]")

        elif node["type"] == "AssignmentExpression" and node["left"]["type"] in ("DeclarativeExpression", "Identifier"):
            expression = node["right"]
            if expression["type"] == "BinaryExpression":
                left, right = check_left_right_expression(expression)
                if left and right:
                    if expression["operator"] == "+" and str(
                            node["left"]["name"] + "=" + left + "+" + right) not in warning:
                        add_check.append((node["left"]["name"], left,
                                          right, expression["start"], expression["end"]))  # (c,a,b)
                        # print("HHHAAAAAAA" + node["left"]["name"])
                        # print(left)
                        # print(right)

                    elif expression["operator"] == "*" and str(
                            node["left"]["name"] + "=" + left + "*" + right) not in warning:
                        mul_check.append((node["left"]["name"], left,
                                          right, expression["start"], expression["end"]))  # (c,a,b)`

                    elif expression["operator"] == "-":
                        arg = (right, left)  # (b, a)
                        # print("PODSDJSDHJSHDSDJDSH" + str(left + "-" + right))
                        # check if assert function has been used for the subtraction op
                        if arg not in ass and str(node["left"]["name"] + "=" + left + "-" + right) not in warning:
                            # print("!!!!!!!!!!!!!!!!" + node["left"]["name"])
                            # print("???????????????????????????????" + str(left + "-" + right))
                            warning.append(str(node["left"]["name"] + "=" + left + "-" + right))
                            # print("Find possible subtraction operation overflow at [", expression["start"],
                            #       expression["end"], "]")

        elif "callee" in node:
            expression = node["callee"]
            if expression["type"] == "Identifier" and expression["name"] == "assert":
                conditions = node["arguments"]
                # check add
                for c in conditions:
                    if c["type"] == "BinaryExpression":
                        # pair = None
                        if c["operator"] == "||":
                            check_mul_helper((c["left"], c["right"]), mul_check)
                            break
                        left, right = check_left_right_expression(c)
                        if left and right:
                            if c["operator"] == ">=" or c["operator"] == ">":
                                pair = (right, left)
                            elif c["operator"] == "<=" or c["operator"] == "<":
                                pair = (left, right)
                            else:
                                break
                        else:
                            break

                        # print("I get pairs!!!!" + "".join(pair))

                        # check if it is used to verify the add op
                        f = True
                        for t in add_check:
                            if (pair[0] == t[1] or pair[0] == t[2]) and pair[1] == t[0]:
                                add_check.remove(t)
                                f = False
                                break
                        for s in sp_add_check:
                            # print(len(sp_add_check))
                            # print("TEST!!!!" + pair[0] + pair[1])
                            # print("Test2!!!" + s[1] + s[0])
                            if pair[0] == s[1] and pair[1] == s[0]:
                                # print("Compare!!!!" + s[1] + s[0])
                                # print(pair[0] + "kakakakaka" + s[1])
                                # print(pair[1] + "sasassasas" + s[0])
                                sp_add_check.remove(s)
                                f = False
                                break
                        for p in sp_mul_check:
                            # print(len(sp_mul_check))
                            # print("TEST!!!!" + pair[0] + pair[1])
                            # print("Test2!!!" + p[1] + p[0])
                            if pair[0] == p[1] and pair[1] == p[0]:
                                sp_mul_check.remove(p)
                                f = False
                                break
                        if f:
                            ass.append(pair)

        else:
            for n in node:
                check_overflow(node[n], ass, add_check, mul_check, sp_add_check, sp_mul_check)
    pass


def check_left_right_expression(c):
    left = get_value_or_name(c["left"])
    right = get_value_or_name(c["right"])

    return left, right


def get_value_or_name(exp):
    if exp["type"] == "Identifier":
        return exp["name"]
    elif exp["type"] == "Literal":
        return str(exp["value"])
    elif exp["type"] == "MemberExpression":
        object = str(get_value_or_name(exp["object"]))
        property = str(get_value_or_name(exp["property"]))
        if object == "msg":
            return str(object + "." + property)
        else:
            return str(object + "[" + property + "]")
    else:
        return None


# def check_left_right_identifier(n):
#     left = get_value_or_name(n["left"])
#     right = get_value_or_name(n["right"])
#     return left, right

# def check_left_identifier(n):
#     left = get_expression(n["left"])
#     return left
#
# def check_right_identifier(n):
#     right = get_expression(n["right"])
#     return right

# def get_expression(exp):
#     if exp["type"] == 'Identifier':
#         return exp["name"]
#     elif exp["type"] == "Literal":
#         return str(exp["value"])
#     elif exp["type"] == "MemberExpression":
#         object = str(get_expression(exp["object"]))
#         property = str(get_expression(exp["property"]))
#         if object == "msg":
#             return str(object + "." + property)
#         else:
#             return str(object + "[" + property + "]")
#     else:
#         return None

def check_mul_helper(exp, mul_check):
    # print("check mul")
    zero = None
    div = None

    for e in exp:

        if e["right"]["type"] == "BinaryExpression" and get_value_or_name(e["left"]) and e["right"]["operator"] == "/":
            left, right = check_left_right_expression(e["right"])
            if left and right:
                div = (left, right, get_value_or_name(e["left"]))

        elif e["left"]["type"] == "BinaryExpression" and get_value_or_name(e["right"]) and e["left"]["operator"] == "/":
            left, right = check_left_right_expression(e["left"])
            if left and right:
                div = (left, right, get_value_or_name(e["right"]))

        elif e["type"] == "BinaryExpression" and e["operator"] == "==":

            z = None
            if e["right"]["type"] == "Literal" and e["right"]["value"] == 0:
                z = e["left"]
            elif e["left"]["type"] == "Literal" and e["left"]["value"] == 0:
                z = e["right"]
            if z:
                zero = get_value_or_name(z)

    if zero and div:
        if zero != div[1]:
            return
        for t in mul_check:
            if (zero == t[1] and div[0] == t[0] and div[2] == t[2]) or (
                    zero == t[2] and div[0] == t[0] and div[2] == t[1]):
                mul_check.remove(t)
                break
